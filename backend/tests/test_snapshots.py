import pytest
from app.models import Organization, SecuritySnapshot
from app.services.snapshot_engine import SnapshotEngine

def test_create_and_compare_snapshots(db_session):
    org = db_session.query(Organization).first()
    engine = SnapshotEngine(db_session, org.id)
    
    # 1. List seeded snapshots
    snapshots = db_session.query(SecuritySnapshot).filter(SecuritySnapshot.organization_id == org.id).order_by(SecuritySnapshot.created_at.asc()).all()
    assert len(snapshots) >= 2
    
    snap1 = snapshots[0]
    snap2 = snapshots[1]
    
    # 2. Compare snapshots
    res = engine.compare_snapshots(snap1.id, snap2.id)
    assert res["score_a"] == snap1.security_posture_score
    assert res["score_b"] == snap2.security_posture_score
    assert res["score_delta"] > 0
    assert res["direction"] == "ESCALATED"
    assert len(res["primary_causes"]) >= 1

def test_create_new_snapshot(db_session):
    org = db_session.query(Organization).first()
    engine = SnapshotEngine(db_session, org.id)
    
    new_snap = engine.create_snapshot("Post-Hardening Audit", "MANUAL_TEST")
    assert new_snap.id is not None
    assert new_snap.snapshot_label == "Post-Hardening Audit"
    assert new_snap.total_applications == 9
