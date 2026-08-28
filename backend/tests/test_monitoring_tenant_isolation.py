"""
test_monitoring_tenant_isolation.py
Tests tenant isolation on Phase 7 Continuous Monitoring endpoints.
"""
import pytest
from app.models import Organization, SecurityIncident, SecurityChange


def test_cross_tenant_incident_access_denial(client, db_session):
    """User from Org A cannot update incident status belonging to Org B."""
    incident = SecurityIncident(
        organization_id="fake-org-b-uuid",
        summary="Org B Secret Incident",
        severity="Critical",
        status="OPEN"
    )
    db_session.add(incident)
    db_session.commit()

    login = client.post("/api/v1/auth/login", json={
        "email": "admin@anurag.tech", "password": "DemoPass123!"
    })
    token = login.cookies.get("access_token")

    res = client.post(
        f"/api/v1/monitoring/incidents/{incident.id}/status",
        json={"status": "RESOLVED"},
        cookies={"access_token": token}
    )
    # Must be denied with 404 Not Found (tenant isolated)
    assert res.status_code == 404
