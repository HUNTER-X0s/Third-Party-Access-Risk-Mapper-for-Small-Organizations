"""
api/v1/endpoints/connectors.py
Connector management API endpoints — Phase 5.

Authorization model:
  VIEWER / AUDITOR: read health and status
  SECURITY_ADMIN:   configure, sync
  SUPER_ADMIN:      full management including disconnect
"""
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import ProviderConnector, ConnectorSyncRun, AuditEvent, User
from app.api.deps import get_current_user, get_current_org_id, require_role
from app.connectors.sync_service import trigger_sync_background

router = APIRouter()

ADMIN_ROLES = ["SUPER_ADMIN", "SECURITY_ADMIN", "IT_ADMIN"]
VIEWER_ROLES = ["SUPER_ADMIN", "SECURITY_ADMIN", "IT_ADMIN", "AUDITOR", "APP_OWNER", "VIEWER"]


# ---- Request/Response Schemas ----

class ConnectorCreateRequest(BaseModel):
    provider: str         # GITHUB, GOOGLE_WORKSPACE, MS365, etc.
    display_name: str
    mode: str = "DEMO"    # DEMO or LIVE
    config: dict = {}     # Non-secret config (app_id, base_url). Credentials from env only.


class ConnectorResponse(BaseModel):
    id: str
    provider: str
    display_name: str
    mode: str
    status: str
    last_sync_at: Optional[str]
    last_error: Optional[str]
    apps_discovered: int
    permissions_discovered: int
    data_freshness_seconds: Optional[int]
    config: dict

    class Config:
        from_attributes = True


class SyncRunResponse(BaseModel):
    id: str
    status: str
    started_at: Optional[str]
    completed_at: Optional[str]
    duration_seconds: Optional[int]
    records_collected: int
    records_normalized: int
    findings_created: int
    snapshot_id: Optional[str]
    error_message: Optional[str]


def _connector_to_response(c: ProviderConnector) -> dict:
    return {
        "id": c.id,
        "provider": c.provider,
        "display_name": c.display_name,
        "mode": c.mode,
        "status": c.status,
        "last_sync_at": c.last_sync_at.isoformat() if c.last_sync_at else None,
        "last_error": c.last_error,
        "apps_discovered": c.apps_discovered or 0,
        "permissions_discovered": c.permissions_discovered or 0,
        "data_freshness_seconds": c.data_freshness_seconds,
        "config": c.config_json or {},
    }


def _sync_run_to_response(r: ConnectorSyncRun) -> dict:
    return {
        "id": r.id,
        "status": r.status,
        "started_at": r.started_at.isoformat() if r.started_at else None,
        "completed_at": r.completed_at.isoformat() if r.completed_at else None,
        "duration_seconds": r.duration_seconds,
        "records_collected": r.records_collected or 0,
        "records_normalized": r.records_normalized or 0,
        "findings_created": r.findings_created or 0,
        "snapshot_id": r.snapshot_id,
        "error_message": r.error_message,
    }


# ---- Endpoints ----

@router.get("")
def list_connectors(
    current_user: User = Depends(require_role(VIEWER_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """List all connectors for the authenticated organization."""
    connectors = db.query(ProviderConnector).filter(
        ProviderConnector.organization_id == org_id
    ).all()
    return [_connector_to_response(c) for c in connectors]


@router.get("/{connector_id}")
def get_connector(
    connector_id: str,
    current_user: User = Depends(require_role(VIEWER_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """Get a specific connector by ID."""
    connector = db.query(ProviderConnector).filter(
        ProviderConnector.id == connector_id,
        ProviderConnector.organization_id == org_id
    ).first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    return _connector_to_response(connector)


@router.post("", status_code=201)
def create_connector(
    req: ConnectorCreateRequest,
    current_user: User = Depends(require_role(ADMIN_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """Configure a new provider connector. Credentials must be in environment variables."""
    # Validate provider
    supported_providers = ["GITHUB"]
    if req.provider.upper() not in supported_providers:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported provider '{req.provider}'. Supported: {supported_providers}"
        )
    if req.mode.upper() not in ("DEMO", "LIVE"):
        raise HTTPException(status_code=400, detail="Mode must be DEMO or LIVE")

    # Prevent duplicate connector per provider per org
    existing = db.query(ProviderConnector).filter(
        ProviderConnector.organization_id == org_id,
        ProviderConnector.provider == req.provider.upper(),
    ).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"A {req.provider.upper()} connector already exists for this organization"
        )

    connector = ProviderConnector(
        organization_id=org_id,
        created_by=current_user.id,
        provider=req.provider.upper(),
        display_name=req.display_name,
        mode=req.mode.upper(),
        status="MISCONFIGURED",
        config_json=req.config,
    )
    db.add(connector)
    db.flush()

    # Audit
    audit = AuditEvent(
        organization_id=org_id,
        actor_email=current_user.email,
        action="CONNECTOR_CONFIGURED",
        target_type="ProviderConnector",
        target_id=connector.id,
        outcome="SUCCESS",
        event_metadata={"provider": req.provider, "mode": req.mode},
    )
    db.add(audit)
    db.commit()
    db.refresh(connector)
    return _connector_to_response(connector)


@router.post("/{connector_id}/sync")
def trigger_sync(
    connector_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_role(ADMIN_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """Trigger a connector synchronization. Runs in background — returns immediately."""
    connector = db.query(ProviderConnector).filter(
        ProviderConnector.id == connector_id,
        ProviderConnector.organization_id == org_id
    ).first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")

    sync_run_id = trigger_sync_background(connector_id, org_id, current_user.email, db)

    return {
        "status": "SYNC_INITIATED",
        "sync_run_id": sync_run_id,
        "connector_id": connector_id,
        "message": "Synchronization started. Check /health for status updates."
    }


@router.get("/{connector_id}/health")
def get_connector_health(
    connector_id: str,
    current_user: User = Depends(require_role(VIEWER_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """Get current connector health and sync status."""
    connector = db.query(ProviderConnector).filter(
        ProviderConnector.id == connector_id,
        ProviderConnector.organization_id == org_id
    ).first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")

    # Data freshness in seconds
    freshness_seconds = None
    if connector.last_sync_at:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        delta = now - connector.last_sync_at
        freshness_seconds = int(delta.total_seconds())

    return {
        "connector_id": connector_id,
        "provider": connector.provider,
        "mode": connector.mode,
        "status": connector.status,
        "last_sync_at": connector.last_sync_at.isoformat() if connector.last_sync_at else None,
        "last_attempted_sync_at": connector.last_attempted_sync_at.isoformat()
            if connector.last_attempted_sync_at else None,
        "last_error": connector.last_error,
        "apps_discovered": connector.apps_discovered or 0,
        "permissions_discovered": connector.permissions_discovered or 0,
        "data_freshness_seconds": freshness_seconds,
        "stale_threshold_seconds": 3600,  # 1 hour
        "is_stale": freshness_seconds is not None and freshness_seconds > 3600,
    }


@router.get("/{connector_id}/last-sync")
def get_last_sync(
    connector_id: str,
    current_user: User = Depends(require_role(["SUPER_ADMIN", "SECURITY_ADMIN", "IT_ADMIN", "AUDITOR"])),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """Get the most recent sync run details."""
    connector = db.query(ProviderConnector).filter(
        ProviderConnector.id == connector_id,
        ProviderConnector.organization_id == org_id
    ).first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")

    last_run = db.query(ConnectorSyncRun).filter(
        ConnectorSyncRun.connector_id == connector_id,
        ConnectorSyncRun.organization_id == org_id
    ).order_by(ConnectorSyncRun.started_at.desc()).first()

    if not last_run:
        return {"message": "No sync runs found for this connector"}
    return _sync_run_to_response(last_run)


@router.post("/{connector_id}/disconnect", status_code=200)
def disconnect_connector(
    connector_id: str,
    current_user: User = Depends(require_role(["SUPER_ADMIN"])),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """
    Disconnect a connector — removes AccessGuard configuration only.
    Does NOT revoke any permissions at the provider (Phase 5 scope).
    """
    connector = db.query(ProviderConnector).filter(
        ProviderConnector.id == connector_id,
        ProviderConnector.organization_id == org_id
    ).first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")

    provider = connector.provider
    db.delete(connector)

    audit = AuditEvent(
        organization_id=org_id,
        actor_email=current_user.email,
        action="CONNECTOR_DISCONNECTED",
        target_type="ProviderConnector",
        target_id=connector_id,
        outcome="SUCCESS",
        event_metadata={
            "provider": provider,
            "note": "AccessGuard configuration removed. No provider-side changes made."
        },
    )
    db.add(audit)
    db.commit()
    return {
        "status": "DISCONNECTED",
        "connector_id": connector_id,
        "note": "Connector configuration removed from AccessGuard. No provider-side changes were made."
    }
