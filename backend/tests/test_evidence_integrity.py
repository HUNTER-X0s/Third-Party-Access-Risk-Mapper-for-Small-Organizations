import pytest
from app.models import RawEvidence, RiskFinding, FindingEvidenceLink, SecurityFact
from app.services.evidence_engine import compute_payload_hash, verify_payload_hash

def test_evidence_hash_determinism():
    payload = {"org": "Anurag", "apps": ["GitHub", "Zapier"], "version": "v1.5.0"}
    h1 = compute_payload_hash(payload)
    h2 = compute_payload_hash(payload)
    assert h1 == h2
    assert len(h1) == 64

def test_evidence_hash_key_order_invariance():
    payload1 = {"a": 1, "b": 2, "c": [1, 2, 3]}
    payload2 = {"c": [1, 2, 3], "b": 2, "a": 1}
    assert compute_payload_hash(payload1) == compute_payload_hash(payload2)

def test_evidence_hash_tamper_detection():
    payload = {"org": "Anurag", "status": "OK"}
    h_orig = compute_payload_hash(payload)
    
    payload_tampered = {"org": "Anurag", "status": "COMPROMISED"}
    h_tampered = compute_payload_hash(payload_tampered)
    
    assert h_orig != h_tampered
    res = verify_payload_hash(payload_tampered, h_orig)
    assert res["is_intact"] is False
    assert res["status"] == "TAMPER_DETECTED"

def test_evidence_verification_endpoint(client, db_session):
    ev = db_session.query(RawEvidence).first()
    assert ev is not None
    
    res = client.get(f"/api/v1/evidence/{ev.id}/verify")
    assert res.status_code == 200
    data = res.json()
    assert data["verification_result"]["is_intact"] is True
    assert data["verification_result"]["status"] == "VERIFIED_INTACT"

def test_finding_to_evidence_traceability(db_session):
    finding = db_session.query(RiskFinding).first()
    assert finding is not None
    
    link = db_session.query(FindingEvidenceLink).filter(FindingEvidenceLink.finding_id == finding.id).first()
    assert link is not None
    
    raw_ev = db_session.query(RawEvidence).filter(RawEvidence.id == link.raw_evidence_id).first()
    assert raw_ev is not None
    assert raw_ev.payload_hash_sha256 is not None
    
    sec_fact = db_session.query(SecurityFact).filter(SecurityFact.raw_evidence_id == raw_ev.id).first()
    assert sec_fact is not None
    assert sec_fact.raw_evidence.evidence_source is not None
