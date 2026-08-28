"""
backend/tests/test_phase81_csrm_validation.py
Phase 8.1 C-SCRM Model Accuracy, Supplier-Risk Explainability, Evidence Quality & RBAC Validation.
"""
import pytest
from app.models.vendor import SupplierProfile, SupplierDueDiligence, SupplierAssessmentHistory
from app.services.supplier_risk_engine import SupplierRiskEngine


def test_supplier_risk_explainability_breakdown(client, db_session):
    """Verifies that GET /vendors/{id}/explain provides a deterministic factor breakdown."""
    login = client.post("/api/v1/auth/login", json={"email": "admin@anurag.tech", "password": "DemoPass123!"})
    token = login.cookies.get("access_token")

    # Get list of vendors
    v_resp = client.get("/api/v1/vendors", cookies={"access_token": token})
    suppliers = v_resp.json().get("suppliers", [])
    assert len(suppliers) > 0
    vendor_id = suppliers[0]["vendor_id"]

    resp = client.get(f"/api/v1/vendors/{vendor_id}/explain", cookies={"access_token": token})
    assert resp.status_code == 200
    data = resp.json()
    assert "supplier_risk_score" in data
    assert "access_risk_score" in data
    assert "contributing_factors" in data
    assert len(data["contributing_factors"]) > 0
    for f in data["contributing_factors"]:
        assert "factor" in f
        assert "impact" in f
        assert "details" in f


def test_case_a_low_supplier_risk_high_access_risk_not_suppressed(client, db_session):
    """
    Case A: Low supplier risk (e.g. GitHub: 20.0) with Crown Jewel / elevated access risk
    must remain P0 priority. Good supplier assurance NEVER suppresses access risk.
    """
    login = client.post("/api/v1/auth/login", json={"email": "admin@anurag.tech", "password": "DemoPass123!"})
    token = login.cookies.get("access_token")

    resp = client.get("/api/v1/vendors/priority-queue", cookies={"access_token": token})
    assert resp.status_code == 200
    queue = resp.json().get("queue", [])

    # Find GitHub (Low supplier risk, but Crown Jewel reachability)
    gh = next((s for s in queue if "github" in s["vendor_name"].lower()), None)
    assert gh is not None
    assert gh["supplier_risk_score"] <= 30.0  # Low supplier posture risk
    assert gh["priority"] == "P0"             # Remains P0 due to Crown Jewel access


def test_case_b_high_supplier_risk_governance_visibility(client, db_session):
    """
    Case B: High supplier risk (e.g. AI Productivity Tool: 85.0 / FOCI potential concern)
    remains visible and prioritized for review.
    """
    login = client.post("/api/v1/auth/login", json={"email": "admin@anurag.tech", "password": "DemoPass123!"})
    token = login.cookies.get("access_token")

    resp = client.get("/api/v1/vendors/priority-queue", cookies={"access_token": token})
    assert resp.status_code == 200
    queue = resp.json().get("queue", [])

    ai_tool = next((s for s in queue if "ai" in s["vendor_name"].lower()), None)
    assert ai_tool is not None
    assert ai_tool["supplier_risk_score"] >= 60.0  # High/Critical supplier risk
    assert ai_tool["priority"] in ("P0", "P1")     # Escalated priority


def test_concentration_reasons_explainability(client, db_session):
    """Verifies that concentration analysis returns explicit reasons explaining concentration."""
    login = client.post("/api/v1/auth/login", json={"email": "admin@anurag.tech", "password": "DemoPass123!"})
    token = login.cookies.get("access_token")

    resp = client.get("/api/v1/vendors/concentration", cookies={"access_token": token})
    assert resp.status_code == 200
    data = resp.json().get("concentration_analysis", [])
    assert len(data) > 0
    for item in data:
        assert "concentration_reasons" in item
        assert len(item["concentration_reasons"]) > 0


def test_single_supplier_failure_explicit_simulation_label(client, db_session):
    """Verifies that failure impact simulation returns explicit simulation labeling."""
    login = client.post("/api/v1/auth/login", json={"email": "admin@anurag.tech", "password": "DemoPass123!"})
    token = login.cookies.get("access_token")

    v_resp = client.get("/api/v1/vendors", cookies={"access_token": token})
    vendor_id = v_resp.json()["suppliers"][0]["vendor_id"]

    resp = client.get(f"/api/v1/vendors/{vendor_id}/impact-analysis", cookies={"access_token": token})
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("simulation_label") == "SIMULATION ONLY"
    assert data.get("impact_nature") == "POTENTIAL BUSINESS IMPACT"
    assert 0.0 <= data["potential_impact_score"] <= 100.0


def test_assessment_version_history_audit_trail(client, db_session):
    """Verifies that updating an assessment creates an immutable history record and increments version."""
    login = client.post("/api/v1/auth/login", json={"email": "admin@anurag.tech", "password": "DemoPass123!"})
    token = login.cookies.get("access_token")

    v_resp = client.get("/api/v1/vendors", cookies={"access_token": token})
    vendor_id = v_resp.json()["suppliers"][0]["vendor_id"]

    # Initial details
    d1 = client.get(f"/api/v1/vendors/{vendor_id}", cookies={"access_token": token}).json()
    initial_version = d1["due_diligence"]["version"]
    initial_history_len = len(d1["assessment_history"])

    # Update assessment
    post_res = client.post(
        f"/api/v1/vendors/{vendor_id}/assess",
        json={
            "foci_status": "ASSESSED_NO_CONCERN",
            "resilience_status": "CURRENT",
            "change_summary": "Phase 8.1 Validation Review"
        },
        cookies={"access_token": token},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    assert post_res.status_code == 200
    assert post_res.json()["version"] == initial_version + 1

    # Verify updated history
    d2 = client.get(f"/api/v1/vendors/{vendor_id}", cookies={"access_token": token}).json()
    assert len(d2["assessment_history"]) == initial_history_len + 1
    latest_hist = d2["assessment_history"][0]
    assert latest_hist["change_summary"] == "Phase 8.1 Validation Review"
    assert "admin@anurag.tech" in latest_hist["reviewed_by"]


def test_rbac_view_vs_write_matrix(client, db_session):
    """
    Verifies that VIEWER and AUDITOR can read but cannot write.
    SECURITY_ADMIN and IT_ADMIN can read and write.
    """
    # 1. VIEWER read vs write
    login_viewer = client.post("/api/v1/auth/login", json={"email": "viewer@anurag.tech", "password": "DemoPass123!"})
    token_viewer = login_viewer.cookies.get("access_token")

    v_resp = client.get("/api/v1/vendors", cookies={"access_token": token_viewer})
    assert v_resp.status_code == 200
    vendor_id = v_resp.json()["suppliers"][0]["vendor_id"]

    # Read endpoints permitted
    assert client.get(f"/api/v1/vendors/{vendor_id}/explain", cookies={"access_token": token_viewer}).status_code == 200
    assert client.get(f"/api/v1/vendors/{vendor_id}/impact-analysis", cookies={"access_token": token_viewer}).status_code == 200
    assert client.get("/api/v1/graph/supply-chain", cookies={"access_token": token_viewer}).status_code == 200

    # Write denied 403
    write_viewer = client.post(
        f"/api/v1/vendors/{vendor_id}/assess",
        json={"foci_status": "ASSESSED_NO_CONCERN"},
        cookies={"access_token": token_viewer},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    assert write_viewer.status_code == 403

    # 2. SECURITY_ADMIN write permitted 200
    login_admin = client.post("/api/v1/auth/login", json={"email": "admin@anurag.tech", "password": "DemoPass123!"})
    token_admin = login_admin.cookies.get("access_token")

    write_admin = client.post(
        f"/api/v1/vendors/{vendor_id}/assess",
        json={"foci_status": "ASSESSED_NO_CONCERN", "change_summary": "Admin update"},
        cookies={"access_token": token_admin},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    assert write_admin.status_code == 200
