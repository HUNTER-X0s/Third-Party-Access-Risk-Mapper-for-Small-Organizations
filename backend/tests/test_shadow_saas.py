"""
test_shadow_saas.py
Tests Shadow SaaS detection, ApplicationBaseline approval workflow, and API endpoint.
"""
import pytest
from app.models import Organization, ApplicationInstance, ApplicationBaseline


def test_shadow_saas_inventory_endpoint(client, db_session):
    """Verifies /api/v1/monitoring/shadow-saas returns authorized vs observed application inventory."""
    login = client.post("/api/v1/auth/login", json={
        "email": "admin@anurag.tech", "password": "DemoPass123!"
    })
    token = login.cookies.get("access_token")

    res = client.get("/api/v1/monitoring/shadow-saas", cookies={"access_token": token})
    assert res.status_code == 200
    data = res.json()

    assert "total_applications" in data
    assert "shadow_saas_count" in data
    assert "inventory" in data
    assert len(data["inventory"]) > 0


def test_approve_application_baseline(client, db_session):
    """Verifies SECURITY_ADMIN can approve or restrict application baselines."""
    login = client.post("/api/v1/auth/login", json={
        "email": "admin@anurag.tech", "password": "DemoPass123!"
    })
    token = login.cookies.get("access_token")

    app = db_session.query(ApplicationInstance).first()

    res = client.post(
        f"/api/v1/monitoring/applications/{app.id}/approve",
        json={"is_approved": True, "approval_status": "APPROVED"},
        cookies={"access_token": token}
    )
    assert res.status_code == 200
    assert res.json()["is_approved"] is True
    assert res.json()["approval_status"] == "APPROVED"
