"""
backend/tests/test_phase71_security.py
Security, Authorization & Tenant Isolation Tests for Phase 7.1 Features.
"""
import pytest
from app.models import SecurityNotification


def test_unauthorized_monitoring_run_denied(client, db_session):
    """Verifies that VIEWER role is denied 403 when trying to trigger POST /monitoring/run."""
    login = client.post("/api/v1/auth/login", json={"email": "viewer@anurag.tech", "password": "DemoPass123!"})
    token = login.cookies.get("access_token")

    res = client.post(
        "/api/v1/monitoring/run",
        cookies={"access_token": token},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    assert res.status_code == 403
    assert "lacks permission" in res.json()["detail"]


def test_authorized_security_admin_can_run_monitoring(client, db_session):
    """Verifies that SECURITY_ADMIN role is permitted to trigger POST /monitoring/run."""
    login = client.post("/api/v1/auth/login", json={"email": "admin@anurag.tech", "password": "DemoPass123!"})
    token = login.cookies.get("access_token")

    res = client.post(
        "/api/v1/monitoring/run",
        cookies={"access_token": token},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    assert res.status_code == 200
    assert res.json()["message"] == "Continuous monitoring evaluation completed successfully"


def test_cross_tenant_notification_isolation(client, db_session):
    """Verifies that Organization A cannot query or mark Org B's notifications as read."""
    notif_b = SecurityNotification(
        organization_id="fake-org-b-uuid",
        title="Org B Confidential Alert",
        body="Secret Org B event",
        severity="Critical",
        notification_type="CRITICAL_PERMISSION_ESCALATION",
        source_type="CHANGE",
        source_id="change-b-001",
        fingerprint="fp-b-unique-001",
        is_read=False
    )
    db_session.add(notif_b)
    db_session.commit()

    login = client.post("/api/v1/auth/login", json={"email": "admin@anurag.tech", "password": "DemoPass123!"})
    token = login.cookies.get("access_token")

    # 1. Listing Org A notifications must not contain Org B
    res_list = client.get("/api/v1/monitoring/notifications", cookies={"access_token": token})
    assert res_list.status_code == 200
    items = res_list.json()
    assert not any(n["id"] == notif_b.id for n in items)

    # 2. Attempting to mark Org B's notification as read by Org A user must return 404
    res_idor = client.post(
        f"/api/v1/monitoring/notifications/{notif_b.id}/read",
        cookies={"access_token": token},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    assert res_idor.status_code == 404
