"""
backend/tests/test_notification_deduplication.py
Tests for Notification Fingerprint Calculation & Deduplication Guarantee.
"""
import pytest
from app.models import Organization, SecurityNotification
from app.services.notification_engine import (
    generate_notification_fingerprint,
    create_notification_if_new
)


def test_notification_fingerprint_deterministic():
    """Verifies that fingerprint generation is strictly deterministic."""
    fp1 = generate_notification_fingerprint("org-123", "CRITICAL_PERMISSION_ESCALATION", "change-456")
    fp2 = generate_notification_fingerprint("org-123", "CRITICAL_PERMISSION_ESCALATION", "change-456")
    fp_diff = generate_notification_fingerprint("org-999", "CRITICAL_PERMISSION_ESCALATION", "change-456")

    assert fp1 == fp2
    assert len(fp1) == 64  # SHA-256 hex length
    assert fp1 != fp_diff


def test_notification_deduplication_engine(db_session):
    """Verifies that create_notification_if_new ignores duplicate events."""
    org = db_session.query(Organization).first()
    assert org is not None

    # First creation
    notif1 = create_notification_if_new(
        db=db_session,
        org_id=org.id,
        notification_type="TEST_ALERT",
        title="Test Escalation Alert",
        body="Details on escalation",
        severity="Critical",
        source_type="CHANGE",
        source_id="unique-source-001"
    )
    assert notif1 is not None
    db_session.flush()

    # Second creation with exact same fingerprint
    notif2 = create_notification_if_new(
        db=db_session,
        org_id=org.id,
        notification_type="TEST_ALERT",
        title="Test Escalation Alert",
        body="Details on escalation",
        severity="Critical",
        source_type="CHANGE",
        source_id="unique-source-001"
    )
    # Deduplication must return None
    assert notif2 is None
