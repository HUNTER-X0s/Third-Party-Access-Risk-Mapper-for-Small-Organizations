"""
backend/tests/test_monitoring_scheduler.py
Tests for Continuous Monitoring Scheduler, Lifecycle, Overlap Locking & Audit Logging.
"""
import pytest
from app.models import Organization, AuditEvent
from app.services.monitoring_scheduler import MonitoringScheduler


def test_scheduler_status_and_metadata(db_session):
    """Verifies that scheduler reports correct metadata (interval, status, last/next run)."""
    scheduler = MonitoringScheduler()
    status = scheduler.get_status()

    assert "monitoring_enabled" in status
    assert "status" in status
    assert "interval_seconds" in status
    assert status["interval_seconds"] == 900


def test_scheduler_run_cycle_and_audit(db_session):
    """Verifies that running a monitoring cycle creates audit events and returns summary."""
    org = db_session.query(Organization).first()
    assert org is not None

    scheduler = MonitoringScheduler()
    result = scheduler.run_cycle_for_org(db_session, org.id, actor_email="test-admin@anurag.tech")

    assert result["status"] == "COMPLETED"
    assert result["organization_id"] == org.id
    assert "changes_detected" in result
    assert "duration_ms" in result

    # Check audit events recorded
    audit_start = db_session.query(AuditEvent).filter(
        AuditEvent.organization_id == org.id,
        AuditEvent.action == "MONITORING_CYCLE_STARTED"
    ).first()
    assert audit_start is not None

    audit_end = db_session.query(AuditEvent).filter(
        AuditEvent.organization_id == org.id,
        AuditEvent.action == "MONITORING_CYCLE_COMPLETED"
    ).first()
    assert audit_end is not None


def test_scheduler_concurrency_overlap_lock(db_session):
    """Verifies that acquiring the lock prevents simultaneous overlapping cycles."""
    org = db_session.query(Organization).first()
    scheduler = MonitoringScheduler()

    # Artificially acquire the scheduler lock
    scheduler._lock.acquire()
    try:
        res = scheduler.run_cycle_for_org(db_session, org.id)
        assert res["status"] == "SKIPPED"
        assert res["reason"] == "CONCURRENT_RUN_IN_PROGRESS"
    finally:
        scheduler._lock.release()
