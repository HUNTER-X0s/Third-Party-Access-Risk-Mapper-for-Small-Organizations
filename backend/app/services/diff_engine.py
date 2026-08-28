"""
app/services/diff_engine.py
Deterministic SecurityDiffEngine for Phase 7 Continuous Monitoring.
Compares Snapshot A vs Snapshot B using stable external/canonical identifiers.
Generates SecurityChange records, calculates Risk Delta, and correlates SecurityIncidents.
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models import (
    SecuritySnapshot, SecurityChange, SecurityIncident, ApplicationInstance,
    PermissionGrant, RiskFinding, DataAsset, ApplicationBaseline, Organization
)

logger = logging.getLogger(__name__)

# Canonical severity hierarchy for permission escalation detection
PERMISSION_SEVERITY_WEIGHTS = {
    "READ": 10,
    "WRITE": 50,
    "ADMIN": 100,
    "UNKNOWN": 30,
}


class SecurityDiffEngine:
    """
    Deterministic change detection engine comparing two trusted SecuritySnapshot states.
    Produces granular SecurityChange records, calculates risk deltas, and correlates incidents.
    """

    def __init__(self, db: Session, organization_id: str):
        self.db = db
        self.org_id = organization_id

    def compare_snapshots(
        self, snapshot_before_id: Optional[str], snapshot_after_id: str
    ) -> Tuple[List[SecurityChange], Optional[SecurityIncident]]:
        """
        Compare snapshot_before vs snapshot_after using stable identifiers.
        Returns a tuple of (List[SecurityChange], Optional[SecurityIncident]).
        """
        snapshot_after = self.db.query(SecuritySnapshot).filter(
            SecuritySnapshot.id == snapshot_after_id,
            SecuritySnapshot.organization_id == self.org_id
        ).first()

        if not snapshot_after:
            raise ValueError(f"Snapshot after '{snapshot_after_id}' not found or unauthorized.")

        snapshot_before = None
        if snapshot_before_id:
            snapshot_before = self.db.query(SecuritySnapshot).filter(
                SecuritySnapshot.id == snapshot_before_id,
                SecuritySnapshot.organization_id == self.org_id
            ).first()

        # Check for existing evaluated changes for this snapshot pair (Idempotency Guarantee)
        existing_changes = self.db.query(SecurityChange).filter(
            SecurityChange.organization_id == self.org_id,
            SecurityChange.snapshot_before_id == snapshot_before_id,
            SecurityChange.snapshot_after_id == snapshot_after_id
        ).all()
        if existing_changes:
            existing_incident = self.db.query(SecurityIncident).filter(
                SecurityIncident.organization_id == self.org_id
            ).order_by(SecurityIncident.detected_at.desc()).first()
            return existing_changes, existing_incident

        manifest_after = snapshot_after.state_manifest_json or {}
        manifest_before = snapshot_before.state_manifest_json if snapshot_before else {}

        apps_before = {a["id"]: a for a in manifest_before.get("applications", [])}
        apps_after = {a["id"]: a for a in manifest_after.get("applications", [])}

        findings_before = {f["id"]: f for f in manifest_before.get("findings", [])}
        findings_after = {f["id"]: f for f in manifest_after.get("findings", [])}

        scopes_before = set(manifest_before.get("excess_scopes", []))
        scopes_after = set(manifest_after.get("excess_scopes", []))

        changes: List[SecurityChange] = []

        # 1. Application Additions & Shadow SaaS Detection
        for app_id, app_data in apps_after.items():
            if app_id not in apps_before:
                # Check baseline for Shadow SaaS
                baseline = self.db.query(ApplicationBaseline).filter(
                    ApplicationBaseline.organization_id == self.org_id,
                    ApplicationBaseline.application_instance_id == app_id
                ).first()

                is_shadow = not (baseline and baseline.is_approved)
                change_type = "SHADOW_SAAS_DETECTED" if is_shadow else "APPLICATION_ADDED"
                severity = "High" if is_shadow else "Low"

                change = SecurityChange(
                    organization_id=self.org_id,
                    snapshot_before_id=snapshot_before_id,
                    snapshot_after_id=snapshot_after_id,
                    change_type=change_type,
                    object_type="APPLICATION",
                    object_id=app_id,
                    object_name=app_data.get("name", "Unknown Application"),
                    source="CONNECTOR_SYNC",
                    severity=severity,
                    confidence="VERIFIED",
                    evidence_refs=[],
                    impact_summary=f"New application '{app_data.get('name')}' observed with risk score {app_data.get('score', 50.0)}.",
                    status="NEW"
                )
                self.db.add(change)
                changes.append(change)

        # 2. Application Removals
        for app_id, app_data in apps_before.items():
            if app_id not in apps_after:
                change = SecurityChange(
                    organization_id=self.org_id,
                    snapshot_before_id=snapshot_before_id,
                    snapshot_after_id=snapshot_after_id,
                    change_type="APPLICATION_REMOVED",
                    object_type="APPLICATION",
                    object_id=app_id,
                    object_name=app_data.get("name", "Unknown Application"),
                    source="CONNECTOR_SYNC",
                    severity="Info",
                    confidence="VERIFIED",
                    evidence_refs=[],
                    impact_summary=f"Application '{app_data.get('name')}' no longer observed in active state.",
                    status="NEW"
                )
                self.db.add(change)
                changes.append(change)

        # 3. Permission Escalation & Reduction
        new_excess_scopes = scopes_after - scopes_before
        removed_excess_scopes = scopes_before - scopes_after

        for scope in new_excess_scopes:
            severity = "Critical" if "admin" in scope.lower() or "write" in scope.lower() else "High"
            change = SecurityChange(
                organization_id=self.org_id,
                snapshot_before_id=snapshot_before_id,
                snapshot_after_id=snapshot_after_id,
                change_type="PERMISSION_ESCALATED",
                object_type="PERMISSION",
                object_id=scope,
                object_name=scope,
                source="CONNECTOR_SYNC",
                severity=severity,
                confidence="VERIFIED",
                evidence_refs=[],
                impact_summary=f"Permission scope '{scope}' escalated or added with excess privilege.",
                status="NEW"
            )
            self.db.add(change)
            changes.append(change)

        for scope in removed_excess_scopes:
            change = SecurityChange(
                organization_id=self.org_id,
                snapshot_before_id=snapshot_before_id,
                snapshot_after_id=snapshot_after_id,
                change_type="PERMISSION_REDUCED",
                object_type="PERMISSION",
                object_id=scope,
                object_name=scope,
                source="CONNECTOR_SYNC",
                severity="Info",
                confidence="VERIFIED",
                evidence_refs=[],
                impact_summary=f"Excess permission scope '{scope}' successfully removed.",
                status="NEW"
            )
            self.db.add(change)
            changes.append(change)

        # 4. Finding Created & Resolved
        for f_id, f_data in findings_after.items():
            if f_id not in findings_before:
                change = SecurityChange(
                    organization_id=self.org_id,
                    snapshot_before_id=snapshot_before_id,
                    snapshot_after_id=snapshot_after_id,
                    change_type="FINDING_CREATED",
                    object_type="FINDING",
                    object_id=f_id,
                    object_name=f_data.get("title", "Risk Finding"),
                    source="CONNECTOR_SYNC",
                    severity=f_data.get("severity", "High"),
                    confidence="VERIFIED",
                    evidence_refs=[],
                    impact_summary=f"New security finding created: '{f_data.get('title')}' ({f_data.get('severity')}).",
                    status="NEW"
                )
                self.db.add(change)
                changes.append(change)

        for f_id, f_data in findings_before.items():
            if f_id not in findings_after:
                change = SecurityChange(
                    organization_id=self.org_id,
                    snapshot_before_id=snapshot_before_id,
                    snapshot_after_id=snapshot_after_id,
                    change_type="FINDING_RESOLVED",
                    object_type="FINDING",
                    object_id=f_id,
                    object_name=f_data.get("title", "Risk Finding"),
                    source="CONNECTOR_SYNC",
                    severity="Info",
                    confidence="VERIFIED",
                    evidence_refs=[],
                    impact_summary=f"Security finding resolved: '{f_data.get('title')}'.",
                    status="NEW"
                )
                self.db.add(change)
                changes.append(change)

        # 5. Risk & Blast Radius Deltas
        risk_before = snapshot_before.security_posture_score if snapshot_before else 50.0
        risk_after = snapshot_after.security_posture_score or 50.0
        risk_delta = round(risk_after - risk_before, 2)

        if risk_delta > 0.1:
            change = SecurityChange(
                organization_id=self.org_id,
                snapshot_before_id=snapshot_before_id,
                snapshot_after_id=snapshot_after_id,
                change_type="RISK_INCREASED",
                object_type="ORGANIZATION",
                object_id=self.org_id,
                object_name="Organization Posture",
                source="CONNECTOR_SYNC",
                severity="Critical" if risk_delta > 15.0 else "High",
                confidence="VERIFIED",
                evidence_refs=[],
                impact_summary=f"Overall risk score increased by +{risk_delta} points (from {risk_before} to {risk_after}).",
                status="NEW"
            )
            self.db.add(change)
            changes.append(change)
        elif risk_delta < -0.1:
            change = SecurityChange(
                organization_id=self.org_id,
                snapshot_before_id=snapshot_before_id,
                snapshot_after_id=snapshot_after_id,
                change_type="RISK_DECREASED",
                object_type="ORGANIZATION",
                object_id=self.org_id,
                object_name="Organization Posture",
                source="CONNECTOR_SYNC",
                severity="Info",
                confidence="VERIFIED",
                evidence_refs=[],
                impact_summary=f"Overall risk score improved by {risk_delta} points (from {risk_before} to {risk_after}).",
                status="NEW"
            )
            self.db.add(change)
            changes.append(change)

        self.db.flush()

        # 6. Correlate Incident if significant changes occurred
        incident = None
        if changes:
            crit_high_count = sum(1 for c in changes if c.severity in ("Critical", "High"))
            incident_severity = "Critical" if any(c.severity == "Critical" for c in changes) else ("High" if crit_high_count > 0 else "Medium")

            summary_text = (
                f"Security sync detected {len(changes)} access change(s) "
                f"including {len(new_excess_scopes)} new permission grant(s) and risk delta of {risk_delta:+0.1f}."
            )

            incident = SecurityIncident(
                organization_id=self.org_id,
                source="CONNECTOR_SYNC",
                severity=incident_severity,
                summary=summary_text,
                change_ids=[c.id for c in changes],
                risk_before=risk_before,
                risk_after=risk_after,
                risk_delta=risk_delta,
                blast_radius_before=40.0,
                blast_radius_after=65.0 if risk_delta > 0 else 40.0,
                status="OPEN"
            )
            self.db.add(incident)
            self.db.flush()

        return changes, incident
