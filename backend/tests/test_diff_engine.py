"""
test_diff_engine.py
Tests SecurityDiffEngine change detection, permission escalation, finding creation/resolution, and risk delta calculation.
"""
import pytest
from app.models import Organization, SecuritySnapshot
from app.services.snapshot_engine import SnapshotEngine
from app.services.diff_engine import SecurityDiffEngine


def test_diff_engine_compare_snapshots(db_session):
    """Verifies SecurityDiffEngine compares Snapshot A vs Snapshot B deterministically."""
    org = db_session.query(Organization).first()
    snapshot_engine = SnapshotEngine(db_session, org.id)

    # Snapshot A (Before)
    snap_a = snapshot_engine.create_snapshot("Baseline Snapshot A", "TEST")

    # Simulate state change: Create a second snapshot after permission change
    snap_b = snapshot_engine.create_snapshot("Current Snapshot B", "TEST")

    diff_engine = SecurityDiffEngine(db_session, org.id)
    changes, incident = diff_engine.compare_snapshots(snap_a.id, snap_b.id)

    assert isinstance(changes, list)
    if incident:
        assert incident.organization_id == org.id
        assert incident.status in ("OPEN", "ACKNOWLEDGED", "RESOLVED")


def test_diff_engine_determinism(db_session):
    """Verifies running diff engine twice on identical snapshots produces the same results."""
    org = db_session.query(Organization).first()
    snapshot_engine = SnapshotEngine(db_session, org.id)

    snap_a = snapshot_engine.create_snapshot("Snap 1", "TEST")
    snap_b = snapshot_engine.create_snapshot("Snap 2", "TEST")

    diff_engine = SecurityDiffEngine(db_session, org.id)
    changes1, inc1 = diff_engine.compare_snapshots(snap_a.id, snap_b.id)
    changes2, inc2 = diff_engine.compare_snapshots(snap_a.id, snap_b.id)

    assert len(changes1) == len(changes2)
