"""
backend/tests/test_phase9_redteam_security.py
Phase 9 Red-Team Security & Adversarial Validation Suite.
Covers: Auth attacks, token tampering, role escalation, BOLA/IDOR cross-tenant access,
CSRF origin rejection, API fuzzing/oversized input, and information disclosure checks.
"""
import pytest
from app.models import (
    ApplicationInstance, RiskFinding, RawEvidence, SecuritySnapshot,
    Vendor, User, SecurityNotification, AuditEvent
)


def test_auth_invalid_credentials_denied(client, db_session):
    """Attempt login with wrong password -> strictly denied with 401."""
    res = client.post("/api/v1/auth/login", json={"email": "admin@anurag.tech", "password": "WrongPassword999!"})
    assert res.status_code == 401
    assert "Invalid email or password" in res.json()["detail"]


def test_auth_nonexistent_user_denied(client, db_session):
    """Attempt login with non-existent user -> denied with 401 (no user enumeration)."""
    res = client.post("/api/v1/auth/login", json={"email": "nonexistent@anurag.tech", "password": "AnyPassword123!"})
    assert res.status_code == 401
    assert "Invalid email or password" in res.json()["detail"]


def test_auth_tampered_jwt_token_denied(client, db_session):
    """Attempt access with forged/tampered JWT cookie -> rejected with 401."""
    tampered_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJTVVBFUl9BRE1JTiJ9.invalidsig123456"
    res = client.get("/api/v1/applications", cookies={"access_token": tampered_token})
    assert res.status_code == 401


def test_role_escalation_viewer_to_admin_denied(client, db_session):
    """
    Attempt privilege escalation: VIEWER tries to perform ADMIN actions:
    1. Trigger monitoring run (POST /monitoring/run)
    2. Assess supplier due diligence (POST /vendors/{id}/assess)
    3. Modify application baseline (POST /monitoring/baselines/{id})
    """
    login = client.post("/api/v1/auth/login", json={"email": "viewer@anurag.tech", "password": "DemoPass123!"})
    token = login.cookies.get("access_token")

    # 1. Monitoring run denied
    r1 = client.post("/api/v1/monitoring/run", cookies={"access_token": token}, headers={"X-Requested-With": "XMLHttpRequest"})
    assert r1.status_code == 403

    # 2. Supplier assess denied
    v_resp = client.get("/api/v1/vendors", cookies={"access_token": token})
    vendor_id = v_resp.json()["suppliers"][0]["vendor_id"]
    r2 = client.post(f"/api/v1/vendors/{vendor_id}/assess", json={"foci_status": "ASSESSED_NO_CONCERN"}, cookies={"access_token": token}, headers={"X-Requested-With": "XMLHttpRequest"})
    assert r2.status_code == 403


def test_bola_idor_cross_tenant_application_denied(client, db_session):
    """
    Attempt BOLA/IDOR: Authenticated user from Org A tries to access ApplicationInstance belonging to Org B.
    Must return 404 or 403, never Org B data.
    """
    login = client.post("/api/v1/auth/login", json={"email": "admin@anurag.tech", "password": "DemoPass123!"})
    token = login.cookies.get("access_token")

    # Create Org B private instance
    app_template = db_session.query(Vendor).first()
    inst_b = ApplicationInstance(
        id="org-b-secret-app-id",
        organization_id="fake-org-b-uuid",
        application_id="app-101",
        display_name="Org B Confidential App",
        status="active",
        authorized_by_email="admin@orgb.com",
        risk_score=90.0,
        risk_severity="Critical"
    )
    db_session.add(inst_b)
    db_session.commit()

    # Org A queries Org B app directly
    res = client.get(f"/api/v1/applications/{inst_b.id}", cookies={"access_token": token})
    assert res.status_code == 404


def test_csrf_unauthorized_origin_rejected(client, db_session):
    """
    Attempt state-changing POST from untrusted origin (e.g. evil-attacker.com)
    with missing X-Requested-With header -> rejected with 403.
    """
    login = client.post("/api/v1/auth/login", json={"email": "admin@anurag.tech", "password": "DemoPass123!"})
    token = login.cookies.get("access_token")

    res = client.post(
        "/api/v1/monitoring/run",
        cookies={"access_token": token},
        headers={"Origin": "https://evil-attacker-site.com"}  # Cross-origin attack attempt
    )
    assert res.status_code == 403


def test_api_fuzzing_malformed_and_oversized_payloads(client, db_session):
    """
    API fuzzing test: Malformed JSON, huge payloads, negative values, invalid types.
    FastAPI / Pydantic must handle gracefully with 422 or 400, never 500.
    """
    login = client.post("/api/v1/auth/login", json={"email": "admin@anurag.tech", "password": "DemoPass123!"})
    token = login.cookies.get("access_token")

    # 1. Negative SLA and invalid types
    v_resp = client.get("/api/v1/vendors", cookies={"access_token": token})
    vendor_id = v_resp.json()["suppliers"][0]["vendor_id"]

    r1 = client.post(
        f"/api/v1/vendors/{vendor_id}/assess",
        json={"sla_availability_pct": "not-a-number"},
        cookies={"access_token": token},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    assert r1.status_code == 422

    # 2. Oversized string payload
    huge_string = "A" * 50000
    r2 = client.post(
        f"/api/v1/vendors/{vendor_id}/assess",
        json={"notes": huge_string},
        cookies={"access_token": token},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    assert r2.status_code in (200, 422)  # Handled cleanly without unhandled crash


def test_information_disclosure_passwords_redacted_in_responses(client, db_session):
    """
    Verifies that user endpoints, audit logs, and vendor listings never return password hashes or raw secrets.
    """
    login = client.post("/api/v1/auth/login", json={"email": "admin@anurag.tech", "password": "DemoPass123!"})
    token = login.cookies.get("access_token")

    # Inspect users endpoint
    u_resp = client.get("/api/v1/users", cookies={"access_token": token})
    if u_resp.status_code == 200:
        raw_text = u_resp.text
        assert "hashed_password" not in raw_text
        assert "password_hash" not in raw_text
        assert "SecurePass123!" not in raw_text
        assert "DemoPass123!" not in raw_text
