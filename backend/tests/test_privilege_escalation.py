import pytest
from app.models import User, Organization
from app.core.security import create_access_token

def test_privilege_escalation_viewer_cannot_update_roles(client, db_session):
    """Verifies that a VIEWER role cannot escalate their own or another user's role."""
    viewer = db_session.query(User).filter(User.email == "viewer@anurag.tech").first()
    assert viewer is not None

    token = create_access_token({"sub": viewer.id, "email": viewer.email, "org_id": viewer.organization_id, "role": viewer.role})
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to upgrade self to SUPER_ADMIN
    res = client.patch(f"/api/v1/users/{viewer.id}/role", json={"role": "SUPER_ADMIN"}, headers=headers)
    assert res.status_code == 403
    assert "lacks permission" in res.json()["detail"]

def test_privilege_escalation_admin_cannot_self_lockout(client, db_session):
    """Verifies that an admin cannot change their own role to prevent accidental lockout."""
    admin = db_session.query(User).filter(User.email == "admin@anurag.tech").first()
    token = create_access_token({"sub": admin.id, "email": admin.email, "org_id": admin.organization_id, "role": admin.role})
    headers = {"Authorization": f"Bearer {token}"}

    res = client.patch(f"/api/v1/users/{admin.id}/role", json={"role": "VIEWER"}, headers=headers)
    assert res.status_code == 400
    assert "Cannot change your own role" in res.json()["detail"]
