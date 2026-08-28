"""
backend/tests/test_notification_center.py
Tests for Notification Center Endpoints, Read/Unread State, Badges & Filters.
"""
import pytest
from app.models import Organization, SecurityNotification


def test_list_notifications_and_counts(client, db_session):
    """Verifies that notification list and unread count endpoints return correct data."""
    org = db_session.query(Organization).first()
    assert org is not None

    # Get count
    res_count = client.get("/api/v1/monitoring/notifications/count")
    assert res_count.status_code == 200
    data_count = res_count.json()
    assert "unread_count" in data_count
    assert "critical_unread_count" in data_count

    # Get list
    res_list = client.get("/api/v1/monitoring/notifications")
    assert res_list.status_code == 200
    items = res_list.json()
    assert isinstance(items, list)
    assert len(items) >= 1

    first = items[0]
    assert "id" in first
    assert "title" in first
    assert "severity" in first
    assert "notification_type" in first
    assert "is_read" in first


def test_mark_notification_read_and_read_all(client, db_session):
    """Verifies marking individual and all notifications as read."""
    org = db_session.query(Organization).first()

    # Get an unread notification
    unread = db_session.query(SecurityNotification).filter(
        SecurityNotification.organization_id == org.id,
        SecurityNotification.is_read == False
    ).first()

    if unread:
        # Mark single as read
        res_read = client.post(f"/api/v1/monitoring/notifications/{unread.id}/read")
        assert res_read.status_code == 200
        assert res_read.json()["is_read"] is True

        db_session.refresh(unread)
        assert unread.is_read is True
        assert unread.read_at is not None

    # Mark all read
    res_all = client.post("/api/v1/monitoring/notifications/read-all")
    assert res_all.status_code == 200

    # Verify unread count is now 0
    res_count = client.get("/api/v1/monitoring/notifications/count")
    assert res_count.json()["unread_count"] == 0
