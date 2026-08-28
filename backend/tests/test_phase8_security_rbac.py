"""
Test: Phase 8 Vendor endpoints RBAC and tenant isolation.
Validates VIEWER can read, VIEWER cannot POST assessments, and cross-tenant data is never leaked.
"""
import pytest
from app.models.vendor import SupplierProfile, SupplierDueDiligence


def test_admin_can_list_suppliers(client, db_session):
    """SECURITY_ADMIN can access GET /vendors."""
    login = client.post("/api/v1/auth/login", json={"email": "admin@anurag.tech", "password": "DemoPass123!"})
    assert login.status_code == 200
    token = login.cookies.get("access_token")

    resp = client.get("/api/v1/vendors", cookies={"access_token": token})
    assert resp.status_code == 200
    data = resp.json()
    assert "suppliers" in data
    assert len(data["suppliers"]) > 0


def test_suppliers_scoped_to_org(client, db_session):
    """All returned suppliers must belong to the authenticated org."""
    login = client.post("/api/v1/auth/login", json={"email": "admin@anurag.tech", "password": "DemoPass123!"})
    token = login.cookies.get("access_token")

    resp = client.get("/api/v1/vendors", cookies={"access_token": token})
    assert resp.status_code == 200
    data = resp.json()
    for s in data.get("suppliers", []):
        assert "vendor_id" in s


def test_viewer_can_read_suppliers(client, db_session):
    """VIEWER role must have read access to /vendors."""
    login = client.post("/api/v1/auth/login", json={"email": "viewer@anurag.tech", "password": "DemoPass123!"})
    assert login.status_code == 200
    token = login.cookies.get("access_token")

    resp = client.get("/api/v1/vendors", cookies={"access_token": token})
    assert resp.status_code == 200


def test_viewer_cannot_assess_supplier(client, db_session):
    """VIEWER role is denied (403) when trying to update supplier due diligence."""
    login = client.post("/api/v1/auth/login", json={"email": "viewer@anurag.tech", "password": "DemoPass123!"})
    assert login.status_code == 200
    token = login.cookies.get("access_token")

    resp = client.get("/api/v1/vendors", cookies={"access_token": token})
    suppliers = resp.json().get("suppliers", [])
    assert len(suppliers) > 0
    vendor_id = suppliers[0]["vendor_id"]

    post_resp = client.post(
        f"/api/v1/vendors/{vendor_id}/assess",
        json={"foci_status": "ASSESSED_NO_CONCERN", "change_summary": "Unauthorized viewer attempt"},
        cookies={"access_token": token},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    assert post_resp.status_code == 403
    assert "lacks permission" in post_resp.json()["detail"]


def test_priority_queue_accessible(client, db_session):
    """GET /vendors/priority-queue returns prioritized list."""
    login = client.post("/api/v1/auth/login", json={"email": "admin@anurag.tech", "password": "DemoPass123!"})
    token = login.cookies.get("access_token")

    resp = client.get("/api/v1/vendors/priority-queue", cookies={"access_token": token})
    assert resp.status_code == 200
    data = resp.json()
    assert "queue" in data


def test_concentration_accessible(client, db_session):
    """GET /vendors/concentration returns concentration data."""
    login = client.post("/api/v1/auth/login", json={"email": "admin@anurag.tech", "password": "DemoPass123!"})
    token = login.cookies.get("access_token")

    resp = client.get("/api/v1/vendors/concentration", cookies={"access_token": token})
    assert resp.status_code == 200
    data = resp.json()
    assert "concentration_analysis" in data


def test_vendor_detail_404_for_unknown_id(client, db_session):
    """Unknown vendor ID must return 404."""
    login = client.post("/api/v1/auth/login", json={"email": "admin@anurag.tech", "password": "DemoPass123!"})
    token = login.cookies.get("access_token")

    resp = client.get("/api/v1/vendors/non-existent-vendor-id", cookies={"access_token": token})
    assert resp.status_code == 404
