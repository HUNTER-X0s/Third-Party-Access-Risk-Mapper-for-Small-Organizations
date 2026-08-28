import pytest
from app.models import User, Organization
from app.core.security import create_access_token

def get_auth_header(client, email):
    res = client.post("/api/v1/auth/login", json={"email": email, "password": "DemoPass123!"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_rbac_security_admin_can_access_users(client, db_session):
    """SECURITY_ADMIN can access user management."""
    headers = get_auth_header(client, "admin@anurag.tech")
    res = client.get("/api/v1/users", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) >= 4

def test_rbac_viewer_denied_user_management(client, db_session):
    """VIEWER role is denied access to user management with 403 Forbidden."""
    headers = get_auth_header(client, "viewer@anurag.tech")
    res = client.get("/api/v1/users", headers=headers)
    assert res.status_code == 403
    assert "lacks permission" in res.json()["detail"]

def test_rbac_auditor_denied_user_management(client, db_session):
    """AUDITOR role is denied access to user management with 403 Forbidden."""
    headers = get_auth_header(client, "auditor@anurag.tech")
    res = client.get("/api/v1/users", headers=headers)
    assert res.status_code == 403

def test_rbac_auditor_can_generate_report(client, db_session):
    """AUDITOR role is authorized to generate executive reports."""
    headers = get_auth_header(client, "auditor@anurag.tech")
    res = client.get("/api/v1/demo/report", headers=headers)
    assert res.status_code == 200
    assert res.json()["report_type"] == "EXECUTIVE_SECURITY_SUMMARY"

def test_rbac_viewer_denied_demo_reset(client, db_session):
    """VIEWER role is denied access to reset demo database."""
    headers = get_auth_header(client, "viewer@anurag.tech")
    res = client.post("/api/v1/demo/reset", headers=headers)
    assert res.status_code == 403
