import pytest
from app.models import Organization, ApplicationInstance

def test_demo_reset_endpoint(client, db_session):
    """Verifies POST /api/v1/demo/reset re-seeds the DB deterministically."""
    res = client.post("/api/v1/demo/reset")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["organization_name"] == "Anurag Technologies"
    assert data["demo_mode"] is True

def test_executive_report_endpoint(client, db_session):
    """Verifies GET /api/v1/demo/report returns formatted report payload."""
    res = client.get("/api/v1/demo/report")
    assert res.status_code == 200
    report = res.json()
    assert report["report_type"] == "EXECUTIVE_SECURITY_SUMMARY"
    assert report["organization_name"] == "Anurag Technologies"
    assert report["security_posture_score"] == 62.4
    assert report["total_monitored_applications"] == 9
    assert report["crown_jewel_assets_count"] == 1
    assert len(report["top_priorities"]) >= 1
    assert "DEMO / SIMULATED ENVIRONMENT" in report["disclaimer"]
