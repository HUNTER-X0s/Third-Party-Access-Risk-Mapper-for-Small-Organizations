"""
app/services/notification_engine.py
Deterministic In-App Notification Engine with Stable Deduplication.
"""
import hashlib
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.monitoring import SecurityNotification, SecurityChange, SecurityIncident


def generate_notification_fingerprint(
    org_id: str,
    notification_type: str,
    source_id: str,
    snapshot_pair: Optional[str] = None
) -> str:
    """
    Generate a stable SHA-256 fingerprint for deduplication.
    Ensures identical security events do not generate duplicate notifications.
    """
    raw = f"{org_id}:{notification_type}:{source_id}:{snapshot_pair or 'none'}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def create_notification_if_new(
    db: Session,
    org_id: str,
    notification_type: str,
    title: str,
    body: str,
    severity: str,
    source_type: str,
    source_id: str,
    snapshot_pair: Optional[str] = None
) -> Optional[SecurityNotification]:
    """
    Creates a SecurityNotification if a notification with the same fingerprint does not already exist.
    """
    fingerprint = generate_notification_fingerprint(org_id, notification_type, source_id, snapshot_pair)
    
    existing = db.query(SecurityNotification).filter(
        SecurityNotification.organization_id == org_id,
        SecurityNotification.fingerprint == fingerprint
    ).first()

    if existing:
        return None

    notification = SecurityNotification(
        organization_id=org_id,
        title=title,
        body=body,
        severity=severity.capitalize(),
        notification_type=notification_type,
        source_type=source_type,
        source_id=source_id,
        fingerprint=fingerprint,
        is_read=False
    )
    db.add(notification)
    db.flush()
    return notification


def process_changes_for_notifications(
    db: Session,
    org_id: str,
    changes: List[SecurityChange],
    incident: Optional[SecurityIncident] = None
) -> List[SecurityNotification]:
    """
    Evaluates a set of changes and/or correlated incident from a monitoring cycle
    and creates deduplicated notifications for significant security events.
    """
    created_notifications = []

    # 1. Incident notification (if high/critical)
    if incident and incident.severity in ("Critical", "High"):
        snapshot_pair = f"{incident.id}"
        notif = create_notification_if_new(
            db=db,
            org_id=org_id,
            notification_type="CORRELATED_SECURITY_INCIDENT",
            title=f"{incident.severity} Security Incident Detected",
            body=incident.summary,
            severity=incident.severity,
            source_type="INCIDENT",
            source_id=incident.id,
            snapshot_pair=snapshot_pair
        )
        if notif:
            created_notifications.append(notif)

    # 2. Individual critical/high changes
    for change in changes:
        if change.severity not in ("Critical", "High"):
            continue

        snapshot_pair = f"{change.snapshot_before_id}:{change.snapshot_after_id}"
        notification_type = None

        if change.change_type == "PERMISSION_ESCALATED":
            notification_type = "CRITICAL_PERMISSION_ESCALATION"
        elif change.change_type == "CROWN_JEWEL_REACHABILITY_CREATED":
            notification_type = "NEW_CROWN_JEWEL_REACHABILITY"
        elif change.change_type == "SHADOW_SAAS_DETECTED":
            notification_type = "HIGH_SHADOW_SAAS"
        elif change.change_type == "RISK_INCREASED" and change.severity == "Critical":
            notification_type = "CRITICAL_RISK_SPIKE"
        elif change.change_type == "NEW_POTENTIAL_ATTACK_PATH":
            notification_type = "NEW_ATTACK_PATH"
        elif change.change_type == "BASELINE_DRIFT":
            notification_type = "BASELINE_DRIFT"

        if notification_type:
            title = f"{change.severity} Alert: {change.change_type.replace('_', ' ').title()}"
            body = change.impact_summary or f"Observed change on {change.object_name or change.object_id}"
            
            notif = create_notification_if_new(
                db=db,
                org_id=org_id,
                notification_type=notification_type,
                title=title,
                body=body,
                severity=change.severity,
                source_type="CHANGE",
                source_id=change.id,
                snapshot_pair=snapshot_pair
            )
            if notif:
                created_notifications.append(notif)

    return created_notifications
