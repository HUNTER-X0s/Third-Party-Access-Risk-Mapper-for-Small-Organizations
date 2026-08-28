"""
connectors/sync_service.py
Background sync lifecycle service.
Orchestrates STARTED → AUTHENTICATING → COLLECTING → NORMALIZING → ANALYZING → COMPLETED/FAILED.
Failure isolation: connector failure never breaks dashboard, demo, graph, or auth.
"""
import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models import ProviderConnector, ConnectorSyncRun, AuditEvent
from app.connectors.github_connector import GitHubConnector, GitHubConnectorConfig
from app.connectors.pipeline import ConnectorPipeline
from app.core.config import settings
from app.db.base_class import utc_now

logger = logging.getLogger(__name__)

# Sync lifecycle status constants
STATUS_STARTED = "STARTED"
STATUS_AUTHENTICATING = "AUTHENTICATING"
STATUS_COLLECTING = "COLLECTING"
STATUS_NORMALIZING = "NORMALIZING"
STATUS_ANALYZING = "ANALYZING"
STATUS_SNAPSHOT_CREATED = "SNAPSHOT_CREATED"
STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED = "FAILED"


def _update_sync_run(db: Session, sync_run: ConnectorSyncRun, status: str,
                      error: str = None) -> None:
    sync_run.status = status
    if error:
        sync_run.error_message = error
    if status in (STATUS_COMPLETED, STATUS_FAILED):
        sync_run.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
        if sync_run.started_at:
            delta = sync_run.completed_at - sync_run.started_at
            sync_run.duration_seconds = int(delta.total_seconds())
    db.flush()


def _update_connector(db: Session, connector: ProviderConnector, status: str,
                       error: str = None, apps: int = 0, perms: int = 0) -> None:
    connector.status = status
    connector.last_attempted_sync_at = datetime.now(timezone.utc).replace(tzinfo=None)
    if error:
        connector.last_error = error
    if status == "HEALTHY":
        connector.last_sync_at = connector.last_attempted_sync_at
        connector.last_error = None
    if apps:
        connector.apps_discovered = apps
    if perms:
        connector.permissions_discovered = perms
    db.flush()


def _audit(db: Session, org_id: str, actor_email: str, action: str,
           connector_id: str, result: str, details: dict = None) -> None:
    event = AuditEvent(
        organization_id=org_id,
        actor_email=actor_email,
        action=action,
        target_type="ProviderConnector",
        target_id=connector_id,
        outcome=result,
        event_metadata=details or {},
    )
    db.add(event)
    db.flush()


async def run_connector_sync(connector_id: str, org_id: str,
                               triggered_by_email: str, db: Session) -> ConnectorSyncRun:
    """
    Execute the full sync lifecycle for a provider connector.
    Isolated from all other system components — failures are contained.
    """
    connector = db.query(ProviderConnector).filter(
        ProviderConnector.id == connector_id,
        ProviderConnector.organization_id == org_id
    ).first()

    if not connector:
        logger.error("Connector %s not found for org %s", connector_id, org_id)
        raise ValueError(f"Connector {connector_id} not found")

    # Create sync run record
    sync_run = ConnectorSyncRun(
        connector_id=connector_id,
        organization_id=org_id,
        triggered_by=triggered_by_email,
        status=STATUS_STARTED,
        started_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    db.add(sync_run)
    db.flush()

    _audit(db, org_id, triggered_by_email, "SYNC_STARTED", connector_id, "SUCCESS",
           {"provider": connector.provider, "sync_run_id": sync_run.id})

    # --- Stage 1: Authenticate ---
    _update_sync_run(db, sync_run, STATUS_AUTHENTICATING)

    if connector.provider == "GITHUB" and connector.mode == "LIVE":
        await _run_github_sync(db, connector, sync_run, org_id, triggered_by_email)
    elif connector.mode == "DEMO":
        await _run_demo_sync(db, connector, sync_run, org_id, triggered_by_email)
    else:
        error = f"Connector mode '{connector.mode}' not supported for provider '{connector.provider}'"
        _update_sync_run(db, sync_run, STATUS_FAILED, error)
        _update_connector(db, connector, "MISCONFIGURED", error)
        _audit(db, org_id, triggered_by_email, "SYNC_FAILED", connector_id, "FAILURE",
               {"error": error})

    db.commit()
    return sync_run


async def _run_github_sync(db: Session, connector: ProviderConnector,
                             sync_run: ConnectorSyncRun, org_id: str,
                             triggered_by_email: str) -> None:
    """Run a live GitHub App sync."""
    # Read credentials from environment — never from database or logs
    app_id = settings.GITHUB_APP_ID
    private_key = settings.GITHUB_PRIVATE_KEY

    if not app_id or not private_key:
        error = "GitHub connector missing GITHUB_APP_ID or GITHUB_PRIVATE_KEY environment variables"
        _update_sync_run(db, sync_run, STATUS_FAILED, error)
        _update_connector(db, connector, "MISCONFIGURED", error)
        _audit(db, org_id, triggered_by_email, "SYNC_FAILED", connector.id, "FAILURE",
               {"error": error})
        return

    github_config = GitHubConnectorConfig(
        app_id=app_id,
        private_key_pem=private_key,
        base_url=settings.GITHUB_BASE_URL,
        api_version=settings.GITHUB_API_VERSION,
    )
    github = GitHubConnector(github_config, connector.id, org_id)

    try:
        auth_ok = await github.authenticate()
        if not auth_ok:
            error = github._last_error or "Authentication failed"
            _update_sync_run(db, sync_run, STATUS_FAILED, error)
            _update_connector(db, connector, "AUTH_FAILED", error)
            _audit(db, org_id, triggered_by_email, "CONNECTOR_AUTH_FAILURE", connector.id, "FAILURE",
                   {"error": error})
            return

        _audit(db, org_id, triggered_by_email, "CONNECTOR_AUTH_SUCCESS", connector.id, "SUCCESS")
        _update_sync_run(db, sync_run, STATUS_COLLECTING)

        installations = await github.discover_installations()
        sync_run.records_collected = len(installations)

        _update_sync_run(db, sync_run, STATUS_NORMALIZING)
        pipeline = ConnectorPipeline(db, org_id, connector.id)
        total_perms = 0
        total_findings = 0

        for inst in installations:
            repos = await github.discover_repositories(inst.installation_id)
            inst.repositories = repos

            raw_payload, evidence_hash = github.build_raw_evidence_payload(inst, repos)
            result = pipeline.process_installation(inst, raw_payload, evidence_hash, sync_run)

            total_perms += len(inst.permissions)
            total_findings += result.get("findings_count", 0)

            if result.get("errors"):
                logger.warning("Pipeline errors for installation %s: %s",
                               inst.installation_id, result["errors"])

        sync_run.records_normalized = len(installations)
        sync_run.findings_created = total_findings

        _update_sync_run(db, sync_run, STATUS_ANALYZING)
        _update_sync_run(db, sync_run, STATUS_COMPLETED)
        _update_connector(db, connector, "HEALTHY", apps=len(installations), perms=total_perms)
        _audit(db, org_id, triggered_by_email, "SYNC_COMPLETED", connector.id, "SUCCESS",
               {"installations": len(installations), "findings": total_findings})

    except Exception as e:
        error = str(e)
        logger.error("GitHub sync failed: %s", error)
        _update_sync_run(db, sync_run, STATUS_FAILED, error)
        _update_connector(db, connector, "DEGRADED", error)
        _audit(db, org_id, triggered_by_email, "SYNC_FAILED", connector.id, "FAILURE",
               {"error": error})
    finally:
        github.close()


async def _run_demo_sync(db: Session, connector: ProviderConnector,
                          sync_run: ConnectorSyncRun, org_id: str,
                          triggered_by_email: str) -> None:
    """
    Demo mode sync — marks connector HEALTHY and updates timestamps.
    Uses existing seeded demo data. No external HTTP calls.
    """
    await asyncio.sleep(0)  # Yield for async consistency
    _update_sync_run(db, sync_run, STATUS_COLLECTING)
    _update_sync_run(db, sync_run, STATUS_NORMALIZING)
    _update_sync_run(db, sync_run, STATUS_COMPLETED)
    _update_connector(db, connector, "HEALTHY", apps=3, perms=12)
    sync_run.records_collected = 3
    sync_run.records_normalized = 3
    _audit(db, org_id, triggered_by_email, "SYNC_COMPLETED", connector.id, "SUCCESS",
           {"mode": "DEMO", "note": "Demo mode sync — no live provider calls"})
    db.flush()


def trigger_sync_background(connector_id: str, org_id: str,
                              triggered_by_email: str, db: Session) -> str:
    """
    Non-blocking sync trigger using asyncio.
    Returns sync run ID immediately; sync executes in background.
    """
    sync_run = ConnectorSyncRun(
        connector_id=connector_id,
        organization_id=org_id,
        triggered_by=triggered_by_email,
        status=STATUS_STARTED,
        started_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    db.add(sync_run)
    db.commit()
    db.refresh(sync_run)

    # Run sync asynchronously without blocking the HTTP response
    async def _run():
        from app.db.session import SessionLocal
        async_db = SessionLocal()
        try:
            await run_connector_sync(connector_id, org_id, triggered_by_email, async_db)
        except Exception as e:
            logger.error("Background sync failed: %s", e)
        finally:
            async_db.close()

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(_run())
    except Exception as e:
        logger.warning("Could not schedule background sync task: %s", e)

    return sync_run.id
