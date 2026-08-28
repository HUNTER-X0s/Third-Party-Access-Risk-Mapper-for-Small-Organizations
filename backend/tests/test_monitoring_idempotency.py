"""
backend/tests/test_monitoring_idempotency.py
Tests for Monitoring Idempotency & Repeat Cycle Consistency.
"""
import pytest
from app.models import Organization, SecurityChange, SecurityIncident, SecurityNotification
from app.services.monitoring_scheduler import MonitoringScheduler


def test_monitoring_cycle_idempotency(db_session):
    """
    Running two consecutive monitoring cycles against the same database state
    must not produce duplicate changes, incidents, or notifications.
    """
    org = db_session.query(Organization).first()
    assert org is not None

    scheduler = MonitoringScheduler()

    # Cycle 1
    res1 = scheduler.run_cycle_for_org(db_session, org.id, actor_email="idempotent-test@anurag.tech")
    assert res1["status"] == "COMPLETED"

    initial_change_count = db_session.query(SecurityChange).filter(
        SecurityChange.organization_id == org.id
    ).count()
    initial_notif_count = db_session.query(SecurityNotification).filter(
        SecurityNotification.organization_id == org.id
    ).count()

    # Cycle 2 (Exact same state)
    res2 = scheduler.run_cycle_for_org(db_session, org.id, actor_email="idempotent-test@anurag.tech")
    assert res2["status"] == "COMPLETED"

    final_change_count = db_session.query(SecurityChange).filter(
        SecurityChange.organization_id == org.id
    ).count()
    final_notif_count = db_session.query(SecurityNotification).filter(
        SecurityNotification.organization_id == org.id
    ).count()

    # Zero duplicate records created
    assert final_change_count == initial_change_count
    assert final_notif_count == initial_notif_count
