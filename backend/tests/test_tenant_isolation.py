import pytest
from app.models import Organization, ApplicationInstance, Application, RiskFinding, RawEvidence, EvidenceSource

def setup_org_b(db_session):
    org_a = db_session.query(Organization).filter(Organization.domain == "anurag.tech").first()
    
    org_b = Organization(name="Beta Cyber Corp", domain="betacyber.com", security_posture_score=90.0)
    db_session.add(org_b)
    db_session.flush()
    
    app_template = db_session.query(Application).first()
    inst_b = ApplicationInstance(
        organization_id=org_b.id,
        application_id=app_template.id,
        display_name="Org B Private Integration",
        status="active",
        authorized_by_email="admin@betacyber.com",
        risk_score=15.0,
        risk_severity="Low"
    )
    db_session.add(inst_b)
    db_session.flush()
    
    ev_src_b = EvidenceSource(organization_id=org_b.id, connector_type="DEMO_SEED")
    db_session.add(ev_src_b)
    db_session.flush()
    
    raw_ev_b = RawEvidence(organization_id=org_b.id, evidence_source_id=ev_src_b.id, payload_hash_sha256="b"*64, raw_payload_json={"org": "B"})
    db_session.add(raw_ev_b)
    db_session.flush()
    
    finding_b = RiskFinding(
        organization_id=org_b.id,
        application_instance_id=inst_b.id,
        finding_type="EXCESS_PERMISSION",
        title="Org B Finding",
        description="Private finding for Org B",
        severity="Low",
        affected_application_name="Org B Private Integration"
    )
    db_session.add(finding_b)
    db_session.commit()
    
    return org_a.id, org_b.id

def test_cross_tenant_application_isolation(client, db_session):
    org_a_id, org_b_id = setup_org_b(db_session)
    
    # As Org B, query applications with X-Organization-ID header
    res_b = client.get("/api/v1/applications", headers={"X-Organization-ID": org_b_id})
    assert res_b.status_code == 200
    apps_b = res_b.json()
    assert len(apps_b) == 1
    assert apps_b[0]["display_name"] == "Org B Private Integration"

    # Verify Org B cannot access Org A's applications directly by ID
    app_a = db_session.query(ApplicationInstance).filter(ApplicationInstance.organization_id == org_a_id).first()
    res_denied = client.get(f"/api/v1/applications/{app_a.id}", headers={"X-Organization-ID": org_b_id})
    assert res_denied.status_code == 404

def test_cross_tenant_finding_isolation(client, db_session):
    org_a_id, org_b_id = setup_org_b(db_session)
    finding_a = db_session.query(RiskFinding).filter(RiskFinding.organization_id == org_a_id).first()
    
    res_denied = client.get(f"/api/v1/findings/{finding_a.id}", headers={"X-Organization-ID": org_b_id})
    assert res_denied.status_code == 404

def test_cross_tenant_evidence_isolation(client, db_session):
    org_a_id, org_b_id = setup_org_b(db_session)
    ev_a = db_session.query(RawEvidence).filter(RawEvidence.organization_id == org_a_id).first()
    
    res_denied = client.get(f"/api/v1/evidence/{ev_a.id}", headers={"X-Organization-ID": org_b_id})
    assert res_denied.status_code == 404
