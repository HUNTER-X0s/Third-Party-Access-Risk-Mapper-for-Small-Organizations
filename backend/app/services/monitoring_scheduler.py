"""
app/services/monitoring_scheduler.py
In-process Periodic Continuous Access Monitoring Scheduler.
"""
import logging
import threading
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import SessionLocal
from app.models import (
    Organization, ProviderConnector, SecuritySnapshot, AuditEvent
)
from app.services.diff_engine import SecurityDiffEngine
from app.services.notification_engine import process_changes_for_notifications
from app.services.snapshot_engine import SnapshotEngine

logger = logging.getLogger("app.services.monitoring_scheduler")


class MonitoringScheduler:
    """
    Lightweight, in-process, thread-safe periodic continuous monitoring scheduler.
    """
    def __init__(self):
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._is_running = False
        self._last_run_at: Optional[datetime] = None
        self._last_status: str = "IDLE"
        self._last_changes_count: int = 0
        self._consecutive_failures: int = 0

    @property
    def is_running(self) -> bool:
        return self._is_running

    def get_status(self, org_id: Optional[str] = None) -> Dict[str, Any]:
        status_label = "ACTIVE" if (self._is_running and settings.MONITORING_ENABLED) else ("PAUSED" if not settings.MONITORING_ENABLED else "IDLE")
        if self._consecutive_failures > 0:
            status_label = "DEGRADED"

        interval = settings.MONITORING_INTERVAL_SECONDS
        next_run = None
        if self._last_run_at and self._is_running:
            next_run = (self._last_run_at + timedelta(seconds=interval)).isoformat()

        return {
            "monitoring_enabled": settings.MONITORING_ENABLED,
            "demo_mode": settings.DEMO_MODE,
            "status": status_label,
            "interval_seconds": interval,
            "last_evaluation_at": self._last_run_at.isoformat() if self._last_run_at else None,
            "next_evaluation_at": next_run,
            "last_changes_detected": self._last_changes_count,
            "consecutive_failures": self._consecutive_failures
        }

    def start(self) -> None:
        if self._is_running:
            return

        if not settings.MONITORING_ENABLED:
            logger.info("Continuous monitoring scheduler is disabled by configuration (MONITORING_ENABLED=False).")
            return

        self._stop_event.clear()
        self._is_running = True
        self._thread = threading.Thread(target=self._worker_loop, daemon=True, name="AccessGuard-MonitoringWorker")
        self._thread.start()
        logger.info("Continuous monitoring scheduler started successfully.")

    def stop(self) -> None:
        if not self._is_running:
            return
        logger.info("Stopping continuous monitoring scheduler...")
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        self._is_running = False
        logger.info("Continuous monitoring scheduler stopped.")

    def _worker_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                self.run_all_organizations()
            except Exception as e:
                logger.error(f"Error in monitoring scheduler worker loop: {e}", exc_info=True)
                self._consecutive_failures += 1

            # Sleep in small increments to respond quickly to stop_event
            interval = settings.MONITORING_INTERVAL_SECONDS
            elapsed = 0
            while elapsed < interval and not self._stop_event.is_set():
                time.sleep(1)
                elapsed += 1

    def run_all_organizations(self) -> None:
        db = SessionLocal()
        try:
            orgs = db.query(Organization).all()
            for org in orgs:
                self.run_cycle_for_org(db, org.id, actor_email="SYSTEM_SCHEDULER")
        finally:
            db.close()

    def run_cycle_for_org(self, db: Session, org_id: str, actor_email: str = "SYSTEM_SCHEDULER") -> Dict[str, Any]:
        """
        Executes a single continuous monitoring evaluation cycle for an organization.
        Thread-safe against concurrent runs on the same organization.
        """
        if not self._lock.acquire(blocking=False):
            logger.warning(f"Monitoring cycle skipped for org {org_id}: another cycle is currently running.")
            return {"status": "SKIPPED", "reason": "CONCURRENT_RUN_IN_PROGRESS"}

        start_time = datetime.now(timezone.utc)
        self._last_run_at = start_time

        # 1. Audit cycle start
        audit_start = AuditEvent(
            organization_id=org_id,
            actor_email=actor_email,
            action="MONITORING_CYCLE_STARTED",
            target_type="Organization",
            target_id=org_id,
            outcome="SUCCESS",
            event_metadata={
                "scheduled": actor_email == "SYSTEM_SCHEDULER",
                "timestamp": start_time.isoformat()
            }
        )
        db.add(audit_start)
        db.commit()

        try:
            # 2. Check connectors and sync if needed
            connectors = db.query(ProviderConnector).filter(
                ProviderConnector.organization_id == org_id,
                ProviderConnector.status == "ACTIVE"
            ).all()

            # 3. Retrieve latest snapshots for comparison
            recent_snapshots = db.query(SecuritySnapshot).filter(
                SecuritySnapshot.organization_id == org_id
            ).order_by(SecuritySnapshot.created_at.desc()).limit(2).all()

            changes = []
            incident = None
            notifications = []

            if len(recent_snapshots) >= 2:
                snap_after = recent_snapshots[0]
                snap_before = recent_snapshots[1]

                # 4. Deterministic diff engine comparison
                diff_engine = SecurityDiffEngine(db, org_id)
                changes, incident = diff_engine.compare_snapshots(snap_before.id, snap_after.id)

                # 5. Process notifications (deduplicated)
                if changes or incident:
                    notifications = process_changes_for_notifications(db, org_id, changes, incident)

            self._last_changes_count = len(changes)
            self._consecutive_failures = 0
            self._last_status = "COMPLETED"

            end_time = datetime.now(timezone.utc)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            # 6. Audit cycle completion
            audit_end = AuditEvent(
                organization_id=org_id,
                actor_email=actor_email,
                action="MONITORING_CYCLE_COMPLETED",
                target_type="Organization",
                target_id=org_id,
                outcome="SUCCESS",
                event_metadata={
                    "connectors_evaluated": len(connectors),
                    "changes_detected": len(changes),
                    "incidents_created": 1 if incident else 0,
                    "notifications_generated": len(notifications),
                    "duration_ms": duration_ms
                }
            )
            db.add(audit_end)
            db.commit()

            return {
                "status": "COMPLETED",
                "organization_id": org_id,
                "changes_detected": len(changes),
                "incident_created": incident.id if incident else None,
                "notifications_generated": len(notifications),
                "duration_ms": duration_ms
            }

        except Exception as e:
            db.rollback()
            self._consecutive_failures += 1
            self._last_status = "FAILED"
            logger.error(f"Monitoring cycle failed for org {org_id}: {e}", exc_info=True)

            audit_fail = AuditEvent(
                organization_id=org_id,
                actor_email=actor_email,
                action="MONITORING_CYCLE_FAILED",
                target_type="Organization",
                target_id=org_id,
                outcome="FAILURE",
                event_metadata={"error": str(e)}
            )
            db.add(audit_fail)
            db.commit()

            return {"status": "FAILED", "error": str(e)}

        finally:
            self._lock.release()


# Global Singleton Scheduler Instance
scheduler = MonitoringScheduler()
