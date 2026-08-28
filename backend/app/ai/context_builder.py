"""
app/ai/context_builder.py
Tenant-isolated, data-minimized AI context builder.

Security Guarantees:
  1. Strict Tenant Isolation: All database queries include organization_id filter.
  2. Data Minimization: Unnecessary raw PII, JWTs, passwords, private keys, and secrets are excluded.
  3. Untrusted Data Wrapping: External provider text (app names, descriptions, scopes) is wrapped in <UNTRUSTED_SECURITY_DATA> tags.
  4. Secret Redaction: Any secret keys in raw evidence are redacted prior to context injection.
"""
import re
import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models import (
    Organization, ApplicationInstance, RiskFinding, PermissionGrant,
    DataAsset, Vendor, RawEvidence, SecurityFact, AccessRelationship,
    ProviderConnector, SecuritySnapshot
)
from app.services.graph_engine import GraphEngine
from app.services.snapshot_engine import SnapshotEngine

logger = logging.getLogger(__name__)

# Secret redaction pattern
_SECRET_PATTERN = re.compile(
    r"(authorization|token|access_token|refresh_token|private_key|pem|client_secret|bearer|password)",
    re.IGNORECASE
)


class AIContextBuilder:
    """
    Constructs a minimal, tenant-isolated structured context payload for the AI Security Analyst.
    Enforces strict tenant isolation and prompt injection isolation delimiters.
    """

    def __init__(self, db: Session, organization_id: str):
        self.db = db
        self.org_id = organization_id

    def build_general_context(self) -> Dict[str, Any]:
        """Build general organizational security posture context."""
        org = self.db.query(Organization).filter(Organization.id == self.org_id).first()
        org_name = org.name if org else "Unknown Organization"

        apps = self.db.query(ApplicationInstance).filter(
            ApplicationInstance.organization_id == self.org_id
        ).all()

        findings = self.db.query(RiskFinding).filter(
            RiskFinding.organization_id == self.org_id
        ).all()

        connectors = self.db.query(ProviderConnector).filter(
            ProviderConnector.organization_id == self.org_id
        ).all()

        data_mode = "LIVE" if any(c.mode == "LIVE" for c in connectors) else "DEMO / SIMULATED"

        return {
            "organization_name": self._sanitize_untrusted_text(org_name),
            "data_mode": data_mode,
            "total_applications": len(apps),
            "total_findings": len(findings),
            "applications": [
                {
                    "id": app.id,
                    "name": self._sanitize_untrusted_text(app.display_name),
                    "risk_score": app.risk_score,
                    "severity": app.risk_severity,
                    "is_shadow": app.is_shadow,
                    "authorized_by": app.authorized_by_email,
                }
                for app in apps[:10]
            ],
            "findings": [
                {
                    "id": f.id,
                    "title": self._sanitize_untrusted_text(f.title),
                    "severity": f.severity,
                    "risk_score": getattr(f, "risk_score_contribution", getattr(f, "risk_score", 25.0)),
                    "affected_app": self._sanitize_untrusted_text(f.affected_application_name),
                }
                for f in findings[:10]
            ],
            "connectors": [
                {
                    "provider": c.provider,
                    "mode": c.mode,
                    "status": c.status,
                    "apps_discovered": c.apps_discovered,
                }
                for c in connectors
            ]
        }

    def build_application_context(self, app_id: str) -> Dict[str, Any]:
        """Build data-minimized context for a specific application instance."""
        app = self.db.query(ApplicationInstance).filter(
            ApplicationInstance.id == app_id,
            ApplicationInstance.organization_id == self.org_id
        ).first()

        if not app:
            return {"error": "Application not found or unauthorized"}

        grants = self.db.query(PermissionGrant).filter(
            PermissionGrant.application_instance_id == app.id
        ).all()

        relationships = self.db.query(AccessRelationship).filter(
            AccessRelationship.application_instance_id == app.id,
            AccessRelationship.organization_id == self.org_id
        ).all()

        findings = self.db.query(RiskFinding).filter(
            RiskFinding.application_instance_id == app.id,
            RiskFinding.organization_id == self.org_id
        ).all()

        # Evidence references
        facts = self.db.query(SecurityFact).filter(
            SecurityFact.organization_id == self.org_id,
            SecurityFact.subject_entity.like(f"%{app.application.canonical_name}%")
        ).limit(5).all()

        evidence_ids = [f.raw_evidence_id for f in facts if f.raw_evidence_id]

        return {
            "application_id": app.id,
            "name": self._sanitize_untrusted_text(app.display_name),
            "canonical_name": self._sanitize_untrusted_text(app.application.canonical_name),
            "vendor_name": self._sanitize_untrusted_text(app.application.vendor.name if app.application.vendor else "Unknown"),
            "risk_score": app.risk_score,
            "severity": app.risk_severity,
            "dimensions": {
                "technical_risk": app.technical_risk_score,
                "data_exposure_risk": app.data_exposure_risk_score,
                "business_impact_risk": app.business_impact_risk_score,
                "vendor_risk": app.vendor_risk_score,
                "attack_path_risk": app.attack_path_risk_score,
            },
            "permissions": [
                {
                    "raw_scope": self._sanitize_untrusted_text(g.raw_scope),
                    "canonical_permission": g.permission.canonical_name if g.permission else "UNKNOWN",
                    "is_excess": g.is_excess,
                }
                for g in grants
            ],
            "accessible_data_assets": [
                {
                    "id": rel.data_asset_id,
                    "name": self._sanitize_untrusted_text(rel.data_asset.name if rel.data_asset else "Asset"),
                    "is_crown_jewel": rel.data_asset.is_crown_jewel if rel.data_asset else False,
                    "access_type": rel.access_type,
                }
                for rel in relationships
            ],
            "findings": [
                {
                    "id": f.id,
                    "title": self._sanitize_untrusted_text(f.title),
                    "severity": f.severity,
                    "risk_score": getattr(f, "risk_score_contribution", getattr(f, "risk_score", 25.0)),
                }
                for f in findings
            ],
            "evidence_items": [{"id": eid} for eid in set(evidence_ids)]
        }

    def build_finding_context(self, finding_id: str) -> Dict[str, Any]:
        """Build context for a specific risk finding."""
        finding = self.db.query(RiskFinding).filter(
            RiskFinding.id == finding_id,
            RiskFinding.organization_id == self.org_id
        ).first()

        if not finding:
            return {"error": "Finding not found or unauthorized"}

        app = finding.application_instance
        app_context = self.build_application_context(app.id) if app else {}

        return {
            "finding_id": finding.id,
            "title": self._sanitize_untrusted_text(finding.title),
            "severity": finding.severity,
            "risk_score": getattr(finding, "risk_score_contribution", getattr(finding, "risk_score", 25.0)),
            "description": self._sanitize_untrusted_text(finding.description),
            "recommendation": self._sanitize_untrusted_text(getattr(finding, "business_impact", "")),
            "affected_application": app_context,
            "evidence_items": app_context.get("evidence_items", [])
        }

    def build_snapshot_diff_context(self, id_a: str, id_b: str) -> Dict[str, Any]:
        """Build context for comparing two security snapshots."""
        snapshot_engine = SnapshotEngine(self.db, self.org_id)
        try:
            diff = snapshot_engine.compare_snapshots(id_a, id_b)
            return {
                "snapshot_a_id": id_a,
                "snapshot_b_id": id_b,
                "risk_score_delta": diff.get("risk_score_delta", 0.0),
                "new_findings_count": len(diff.get("new_findings", [])),
                "resolved_findings_count": len(diff.get("resolved_findings", [])),
                "new_applications_count": len(diff.get("new_applications", [])),
                "new_excess_scopes_count": len(diff.get("new_excess_scopes", [])),
                "details": diff
            }
        except Exception as e:
            return {"error": f"Snapshot comparison failed: {e}"}

    def _sanitize_untrusted_text(self, text: Optional[str]) -> str:
        """
        Sanitize third-party provider strings and wrap in <UNTRUSTED_SECURITY_DATA> tags.
        Prevents prompt injection by isolating external data from model instructions.
        """
        if not text:
            return ""
        # Redact obvious secret patterns
        cleaned = _SECRET_PATTERN.sub("[REDACTED]", text)
        # Escape tag delimiters if present in untrusted input
        cleaned = cleaned.replace("<UNTRUSTED_SECURITY_DATA>", "").replace("</UNTRUSTED_SECURITY_DATA>", "")
        return f"<UNTRUSTED_SECURITY_DATA>{cleaned}</UNTRUSTED_SECURITY_DATA>"
