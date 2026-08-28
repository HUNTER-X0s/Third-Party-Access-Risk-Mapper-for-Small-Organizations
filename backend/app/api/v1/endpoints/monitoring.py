"""
api/v1/endpoints/monitoring.py
Continuous Security Monitoring, Change Detection, Incidents, Shadow SaaS, Notifications & Scheduler.

Authorization & Governance:
  1. Authenticated Users Only (get_current_user).
  2. Organization ID derived exclusively from authenticated user token.
  3. Strict Tenant Isolation on all database queries.
  4. RBAC Roles checked:
     - VIEWER / AUDITOR / APP_OWNER: View changes, incidents, shadow apps, notifications
     - SECURITY_ADMIN / SUPER_ADMIN / IT_ADMIN: Run manual checks, manage incident status & approve baselines
"""
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.models import (
    User, SecurityChange, SecurityIncident, ApplicationBaseline, ApplicationInstance,
    SecurityNotification, AuditEvent
)
from app.api.deps import get_current_user, get_current_org_id, require_role
from app.services.monitoring_scheduler import scheduler

router = APIRouter()

ALLOWED_ROLES = ["SUPER_ADMIN", "SECURITY_ADMIN", "IT_ADMIN", "AUDITOR", "APP_OWNER", "VIEWER"]
ADMIN_ROLES = ["SUPER_ADMIN", "SECURITY_ADMIN"]
RUN_CHECK_ROLES = ["SUPER_ADMIN", "SECURITY_ADMIN", "IT_ADMIN"]


class IncidentStatusUpdate(BaseModel):
    status: str  # OPEN, ACKNOWLEDGED, INVESTIGATING, MITIGATED, RESOLVED, DISMISSED


class ApplicationApprovalRequest(BaseModel):
    is_approved: bool
    approval_status: str = "APPROVED"  # APPROVED, RESTRICTED, REJECTED


# ── Security Changes & Incidents ──────────────────────────────────────────

@router.get("/changes")
def get_security_changes(
    severity: Optional[str] = None,
    change_type: Optional[str] = None,
    object_id: Optional[str] = None,
    limit: int = Query(50, le=200),
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """List detected security changes for the organization."""
    query = db.query(SecurityChange).filter(SecurityChange.organization_id == org_id)

    if severity:
        query = query.filter(SecurityChange.severity == severity.capitalize())
    if change_type:
        query = query.filter(SecurityChange.change_type == change_type)
    if object_id:
        query = query.filter(SecurityChange.object_id == object_id)

    changes = query.order_by(SecurityChange.timestamp.desc()).limit(limit).all()

    return [
        {
            "id": c.id,
            "change_type": c.change_type,
            "object_type": c.object_type,
            "object_id": c.object_id,
            "object_name": c.object_name,
            "timestamp": c.timestamp.isoformat() if c.timestamp else None,
            "source": c.source,
            "severity": c.severity,
            "confidence": c.confidence,
            "evidence_refs": c.evidence_refs or [],
            "impact_summary": c.impact_summary,
            "status": c.status,
            "snapshot_before_id": c.snapshot_before_id,
            "snapshot_after_id": c.snapshot_after_id,
        }
        for c in changes
    ]


@router.get("/incidents")
def get_security_incidents(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """List correlated security incidents for the organization."""
    query = db.query(SecurityIncident).filter(SecurityIncident.organization_id == org_id)

    if status_filter:
        query = query.filter(SecurityIncident.status == status_filter.upper())

    incidents = query.order_by(SecurityIncident.detected_at.desc()).all()

    return [
        {
            "id": inc.id,
            "detected_at": inc.detected_at.isoformat() if inc.detected_at else None,
            "source": inc.source,
            "severity": inc.severity,
            "summary": inc.summary,
            "change_count": len(inc.change_ids or []),
            "risk_before": inc.risk_before,
            "risk_after": inc.risk_after,
            "risk_delta": inc.risk_delta,
            "status": inc.status,
        }
        for inc in incidents
    ]


@router.post("/incidents/{incident_id}/status")
def update_incident_status(
    incident_id: str,
    body: IncidentStatusUpdate,
    current_user: User = Depends(require_role(ADMIN_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """Update lifecycle status of a correlated security incident (Security Admin only)."""
    incident = db.query(SecurityIncident).filter(
        SecurityIncident.id == incident_id,
        SecurityIncident.organization_id == org_id
    ).first()

    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found or unauthorized.")

    incident.status = body.status.upper()
    db.commit()
    return {"message": "Incident status updated successfully", "incident_id": incident.id, "status": incident.status}


# ── Shadow SaaS & Baselines ───────────────────────────────────────────────

@router.get("/shadow-saas")
def get_shadow_saas_inventory(
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """List Shadow SaaS vs Authorized application intelligence."""
    apps = db.query(ApplicationInstance).filter(ApplicationInstance.organization_id == org_id).all()

    inventory = []
    for app in apps:
        baseline = db.query(ApplicationBaseline).filter(
            ApplicationBaseline.organization_id == org_id,
            ApplicationBaseline.application_instance_id == app.id
        ).first()

        is_approved = baseline.is_approved if baseline else app.approved_by_admin
        approval_status = baseline.approval_status if baseline else ("APPROVED" if app.approved_by_admin else "UNAPPROVED")

        inventory.append({
            "application_id": app.id,
            "name": app.display_name,
            "vendor_name": app.application.vendor.name if app.application and app.application.vendor else "Unknown",
            "risk_score": app.risk_score,
            "severity": app.risk_severity,
            "is_shadow": not is_approved,
            "approval_status": approval_status,
            "authorized_by": app.authorized_by_email,
            "first_seen_at": baseline.first_seen_at.isoformat() if baseline and baseline.first_seen_at else app.authorized_at.isoformat() if app.authorized_at else None,
            "last_seen_at": baseline.last_seen_at.isoformat() if baseline and baseline.last_seen_at else app.last_activity_at.isoformat() if app.last_activity_at else None,
        })

    return {
        "organization_id": org_id,
        "total_applications": len(inventory),
        "shadow_saas_count": sum(1 for item in inventory if item["is_shadow"]),
        "inventory": inventory
    }


@router.post("/applications/{app_id}/approve")
def approve_application_baseline(
    app_id: str,
    body: ApplicationApprovalRequest,
    current_user: User = Depends(require_role(ADMIN_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """Approve or restrict application baseline (Security Admin only)."""
    app = db.query(ApplicationInstance).filter(
        ApplicationInstance.id == app_id,
        ApplicationInstance.organization_id == org_id
    ).first()

    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application instance not found or unauthorized.")

    baseline = db.query(ApplicationBaseline).filter(
        ApplicationBaseline.organization_id == org_id,
        ApplicationBaseline.application_instance_id == app.id
    ).first()

    if not baseline:
        baseline = ApplicationBaseline(
            organization_id=org_id,
            application_instance_id=app.id,
        )
        db.add(baseline)

    baseline.is_approved = body.is_approved
    baseline.approval_status = body.approval_status
    baseline.approved_by_user_id = current_user.id
    baseline.approved_at = datetime.now(timezone.utc)

    # Sync app instance model flag
    app.approved_by_admin = body.is_approved
    app.is_shadow = not body.is_approved

    db.commit()

    return {
        "message": f"Application baseline updated to {body.approval_status}",
        "application_id": app.id,
        "is_approved": body.is_approved,
        "approval_status": body.approval_status
    }


# ── Notification Center ───────────────────────────────────────────────────

@router.get("/notifications")
def get_notifications(
    is_read: Optional[bool] = None,
    severity: Optional[str] = None,
    notification_type: Optional[str] = None,
    limit: int = Query(50, le=100),
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """List in-app notifications for the organization."""
    query = db.query(SecurityNotification).filter(SecurityNotification.organization_id == org_id)

    if is_read is not None:
        query = query.filter(SecurityNotification.is_read == is_read)
    if severity:
        query = query.filter(SecurityNotification.severity == severity.capitalize())
    if notification_type:
        query = query.filter(SecurityNotification.notification_type == notification_type)

    notifications = query.order_by(SecurityNotification.created_at.desc()).limit(limit).all()

    return [
        {
            "id": n.id,
            "title": n.title,
            "body": n.body,
            "severity": n.severity,
            "notification_type": n.notification_type,
            "source_type": n.source_type,
            "source_id": n.source_id,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
            "read_at": n.read_at.isoformat() if n.read_at else None,
        }
        for n in notifications
    ]


@router.get("/notifications/count")
def get_unread_notification_count(
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """Get count of unread notifications for badge rendering."""
    count = db.query(SecurityNotification).filter(
        SecurityNotification.organization_id == org_id,
        SecurityNotification.is_read == False
    ).count()

    critical_count = db.query(SecurityNotification).filter(
        SecurityNotification.organization_id == org_id,
        SecurityNotification.is_read == False,
        SecurityNotification.severity == "Critical"
    ).count()

    return {
        "organization_id": org_id,
        "unread_count": count,
        "critical_unread_count": critical_count
    }


@router.post("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """Mark a specific notification as read."""
    notification = db.query(SecurityNotification).filter(
        SecurityNotification.id == notification_id,
        SecurityNotification.organization_id == org_id
    ).first()

    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found or unauthorized.")

    notification.is_read = True
    notification.read_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Notification marked as read", "id": notification.id, "is_read": True}


@router.post("/notifications/read-all")
def mark_all_notifications_read(
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """Mark all notifications as read for the user's organization."""
    now = datetime.now(timezone.utc)
    updated = db.query(SecurityNotification).filter(
        SecurityNotification.organization_id == org_id,
        SecurityNotification.is_read == False
    ).update({"is_read": True, "read_at": now})
    db.commit()

    return {"message": f"{updated} notifications marked as read", "updated_count": updated}


# ── Monitoring Scheduler & Manual Evaluation ──────────────────────────────

@router.get("/status")
def get_monitoring_status(
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
    org_id: str = Depends(get_current_org_id),
):
    """Returns continuous monitoring status and schedule metadata."""
    return scheduler.get_status(org_id)


@router.post("/run")
def trigger_manual_monitoring_check(
    current_user: User = Depends(require_role(RUN_CHECK_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """
    Triggers an immediate continuous monitoring evaluation cycle (Authorized Roles: Security Admin, Super Admin, IT Admin).
    """
    # Audit manual run request
    audit_req = AuditEvent(
        organization_id=org_id,
        actor_email=current_user.email,
        action="MONITORING_RUN_REQUESTED",
        target_type="Organization",
        target_id=org_id,
        outcome="SUCCESS",
        event_metadata={"actor_role": current_user.role}
    )
    db.add(audit_req)
    db.commit()

    result = scheduler.run_cycle_for_org(db, org_id, actor_email=current_user.email)

    if result.get("status") == "FAILED":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Monitoring run failed: {result.get('error')}"
        )

    return {
        "message": "Continuous monitoring evaluation completed successfully",
        "result": result
    }


# ── Unified Security Timeline ─────────────────────────────────────────────

@router.get("/timeline")
def get_security_timeline(
    limit: int = Query(50, le=200),
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """Unified security access timeline combining changes, incidents, and audit events."""
    changes = db.query(SecurityChange).filter(
        SecurityChange.organization_id == org_id
    ).order_by(SecurityChange.timestamp.desc()).limit(limit).all()

    timeline_items = [
        {
            "id": c.id,
            "type": "CHANGE",
            "event_type": c.change_type,
            "title": f"{c.change_type.replace('_', ' ')} on {c.object_name or c.object_id}",
            "severity": c.severity,
            "timestamp": c.timestamp.isoformat() if c.timestamp else None,
            "summary": c.impact_summary,
        }
        for c in changes
    ]

    return {"organization_id": org_id, "timeline": timeline_items}
