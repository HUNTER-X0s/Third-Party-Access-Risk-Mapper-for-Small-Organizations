"""
test_incident_correlation.py
Tests SecurityIncident correlation and incident status lifecycle endpoints.
"""
import pytest
from app.models import Organization, SecurityIncident


def test_get_security_incidents_endpoint(client, db_session):
    """Verifies /api/v1/monitoring/incidents endpoint returns correlated security incidents."""
    login = client.post("/api/v1/auth/login", json={
        "email": "admin@anurag.tech", "password": "DemoPass123!"
    })
    token = login.cookies.get("access_token")

    res = client.get("/api/v1/monitoring/incidents", cookies={"access_token": token})
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_update_incident_status_endpoint(client, db_session):
    """Verifies SECURITY_ADMIN can update incident status."""
    org = db_session.query(Organization).first()
    incident = SecurityIncident(
        organization_id=org.id,
        summary="Test Security Incident",
        severity="High",
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
        json={"status": "INVESTIGATING"},
        cookies={"access_token": token}
    )
    assert res.status_code == 200
    assert res.json()["status"] == "INVESTIGATING"
