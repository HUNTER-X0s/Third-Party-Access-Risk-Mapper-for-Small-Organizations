"""
connectors/pipeline.py
Normalization Pipeline: Raw Provider Data → Evidence → Domain → Risk → Snapshot.

Pipeline stages:
  1. Raw data + secret redaction → RawEvidence (SHA-256 hash)
  2. RawEvidence → SecurityFacts
  3. NormalizedInstallation → Domain objects (Vendor, Application, ApplicationInstance,
     PermissionGrant, AccessRelationship, DataAsset)
  4. Domain objects → RiskEngine.evaluate() → RiskFinding[]
  5. RiskEngine output → SnapshotEngine.create_snapshot()

Critical: Does NOT modify risk_engine_v1.5.0. Same engine handles demo + live data.
"""
import logging
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.connectors.models import NormalizedInstallation, NormalizedRepository, SyncResult
from app.connectors.normalization import redact_secrets, compute_evidence_hash
from app.models import (
    Organization, Vendor, Application, ApplicationInstance, PermissionGrant,
    Permission, ProviderScope, EvidenceSource, RawEvidence, SecurityFact,
    DataAsset, AccessRelationship, DataClassification, ProviderConnector, ConnectorSyncRun,
    SecuritySnapshot
)
from app.models.audit import AuditEvent
from app.services.snapshot_engine import SnapshotEngine
from app.services.diff_engine import SecurityDiffEngine
from app.db.base_class import generate_uuid

logger = logging.getLogger(__name__)


class ConnectorPipeline:
    """
    Orchestrates the full normalization and domain-integration pipeline.
    Each step is isolated: a failure in risk evaluation does not break evidence capture.
    """

    def __init__(self, db: Session, org_id: str, connector_id: str):
        self.db = db
        self.org_id = org_id
        self.connector_id = connector_id

    # ------------------------------------------------------------------
    # Stage 1: Evidence Capture
    # ------------------------------------------------------------------

    def capture_evidence(self, redacted_payload: dict, evidence_hash: str,
                          source_label: str = "github_app_installation") -> RawEvidence:
        """Store redacted raw provider payload as tamper-evident RawEvidence."""
        # Find or create EvidenceSource for this connector
        source = self.db.query(EvidenceSource).filter(
            EvidenceSource.organization_id == self.org_id,
            EvidenceSource.connector_instance_id == self.connector_id
        ).first()

        if not source:
            source = EvidenceSource(
                organization_id=self.org_id,
                connector_type="GITHUB",
                connector_instance_id=self.connector_id,
                api_endpoint=f"github://app/installations/{source_label}",
                authenticated_identity="github-app",
                trust_level="VERIFIED_API",
            )
            self.db.add(source)
            self.db.flush()

        evidence = RawEvidence(
            organization_id=self.org_id,
            evidence_source_id=source.id,
            payload_hash_sha256=evidence_hash,
            raw_payload_json=redacted_payload,
            data_freshness_status="CONFIRMED",
        )
        self.db.add(evidence)
        self.db.flush()
        return evidence

    # ------------------------------------------------------------------
    # Stage 2: Security Facts
    # ------------------------------------------------------------------

    def create_security_facts(self, installation: NormalizedInstallation,
                               evidence: RawEvidence) -> List[SecurityFact]:
        """Generate SecurityFacts from a normalized installation."""
        facts = []

        # GITHUB_APP_INSTALLED fact
        fact_installed = SecurityFact(
            organization_id=self.org_id,
            raw_evidence_id=evidence.id,
            fact_type="GITHUB_APP_INSTALLED",
            subject_entity=f"github:{installation.app_slug}:{installation.account_login}",
            fact_details={
                "installation_id": installation.installation_id,
                "account_login": installation.account_login,
                "account_type": installation.account_type,
                "repository_selection": installation.repository_selection.value,
                "is_suspended": installation.is_suspended,
                "normalization_version": "1.0.0",
            },
        )
        self.db.add(fact_installed)
        facts.append(fact_installed)

        # GITHUB_INSTALLATION_SUSPENDED fact (if applicable)
        if installation.is_suspended:
            fact_suspended = SecurityFact(
                organization_id=self.org_id,
                raw_evidence_id=evidence.id,
                fact_type="GITHUB_INSTALLATION_SUSPENDED",
                subject_entity=f"github:{installation.app_slug}:{installation.account_login}",
                fact_details={"suspension_reason": installation.suspension_reason},
            )
            self.db.add(fact_suspended)
            facts.append(fact_suspended)

        # GITHUB_PERMISSION_GRANTED facts (one per normalized permission)
        for perm in installation.permissions:
            fact_perm = SecurityFact(
                organization_id=self.org_id,
                raw_evidence_id=evidence.id,
                fact_type="GITHUB_PERMISSION_GRANTED",
                subject_entity=f"github:{installation.app_slug}:{installation.account_login}",
                fact_details={
                    "raw_key": perm.raw_provider_key,
                    "raw_value": perm.raw_provider_value,
                    "canonical_permission": perm.canonical_permission.value,
                    "normalization_status": perm.normalization_status.value,
                    "severity": perm.severity,
                    "normalization_version": perm.normalization_version,
                },
            )
            self.db.add(fact_perm)
            facts.append(fact_perm)

        # GITHUB_REPOSITORY_ACCESS facts (one per repository)
        for repo in installation.repositories:
            fact_repo = SecurityFact(
                organization_id=self.org_id,
                raw_evidence_id=evidence.id,
                fact_type="GITHUB_REPOSITORY_ACCESS",
                subject_entity=f"github:{installation.app_slug}:{repo.full_name}",
                fact_details={
                    "repository_id": repo.external_id,
                    "full_name": repo.full_name,
                    "visibility": repo.visibility,
                    "is_private": repo.is_private,
                    "classification": repo.classification,
                },
            )
            self.db.add(fact_repo)
            facts.append(fact_repo)

        self.db.flush()
        return facts

    # ------------------------------------------------------------------
    # Stage 3: Domain Mapping
    # ------------------------------------------------------------------

    def map_to_domain(self, installation: NormalizedInstallation,
                       evidence: RawEvidence) -> Optional[ApplicationInstance]:
        """
        Map a normalized GitHub installation to AccessGuard domain objects.
        Uses stable external IDs to prevent duplicates across syncs (idempotent).
        Business Purpose: UNCLASSIFIED/REQUIRES_REVIEW for live-discovered apps.
        """
        # Idempotency: find or create Vendor by stable external slug
        vendor = self.db.query(Vendor).filter(
            Vendor.name == f"GitHub ({installation.account_login})"
        ).first()
        if not vendor:
            vendor = Vendor(
                name=f"GitHub ({installation.account_login})",
                website="https://github.com",
                soc2_status="unknown",
                trust_score=70.0,
            )
            self.db.add(vendor)
            self.db.flush()

        # Find or create Application with stable external ID in description
        external_app_key = f"github-app-{installation.app_id}-{installation.account_login}"
        app = self.db.query(Application).filter(
            Application.description.like(f"%{external_app_key}%")
        ).first()
        if not app:
            app = Application(
                vendor_id=vendor.id,
                canonical_name=f"GitHub App — {installation.app_slug}",
                category="Dev",
                provider_type="github",
                description=f"GitHub App integration. External key: {external_app_key}. Business Purpose: UNCLASSIFIED/REQUIRES_REVIEW",
            )
            self.db.add(app)
            self.db.flush()

        # Find or create ApplicationInstance (stable by external installation_id)
        external_inst_key = f"github-installation-{installation.installation_id}"
        instance = self.db.query(ApplicationInstance).filter(
            ApplicationInstance.organization_id == self.org_id,
            ApplicationInstance.display_name.like(f"%{external_inst_key}%")
        ).first()

        if not instance:
            instance = ApplicationInstance(
                organization_id=self.org_id,
                application_id=app.id,
                display_name=f"GitHub App ({installation.app_slug}) [{external_inst_key}]",
                status="active",
                authorized_by_email="live-connector@accessguard",
                approved_by_admin=False,  # Requires admin review for live apps
                risk_score=50.0,
                risk_severity="Medium",
            )
            self.db.add(instance)
            self.db.flush()

        # Refresh to get the latest relationship state from DB before dedup check
        self.db.refresh(instance)

        # Create PermissionGrants from normalized permissions (idempotent via flush)
        existing_grant_keys = {
            (g.permission_id, g.application_instance_id)
            for g in instance.permission_grants
        }

        for norm_perm in installation.permissions:
            # Find or create Permission record (canonical_name is unique)
            perm_record = self.db.query(Permission).filter(
                Permission.canonical_name == norm_perm.canonical_permission.value
            ).first()
            if not perm_record:
                perm_record = Permission(
                    canonical_name=norm_perm.canonical_permission.value,
                    display_name=f"Permission {norm_perm.canonical_permission.value}",
                    category=norm_perm.canonical_permission.value,
                    severity_level=norm_perm.severity.capitalize(),
                    description=norm_perm.notes or "",
                )
                self.db.add(perm_record)
                self.db.flush()

            if (perm_record.id, instance.id) not in existing_grant_keys:
                grant = PermissionGrant(
                    application_instance_id=instance.id,
                    permission_id=perm_record.id,
                    raw_scope=f"{norm_perm.raw_provider_key}:{norm_perm.raw_provider_value}",
                    is_excess=norm_perm.severity in ("CRITICAL", "HIGH"),
                    granted_at=datetime.now(timezone.utc),
                )
                self.db.add(grant)

        # Create DataAssets for repositories
        for repo in installation.repositories:
            existing_asset = self.db.query(DataAsset).filter(
                DataAsset.organization_id == self.org_id,
                DataAsset.name == repo.full_name,
            ).first()
            if not existing_asset:
                data_class = self.db.query(DataClassification).first()
                if not data_class:
                    data_class = DataClassification(
                        name="Intellectual Property",
                        display_name="Source Code & IP",
                        sensitivity_level=5,
                        color_code="#ef4444"
                    )
                    self.db.add(data_class)
                    self.db.flush()

                asset = DataAsset(
                    organization_id=self.org_id,
                    classification_id=data_class.id,
                    name=repo.full_name,
                    system_of_record="GitHub",
                    is_crown_jewel=repo.is_private and repo.classification == "CROWN_JEWEL",
                    description=f"GitHub repository: {repo.full_name}",
                )
                self.db.add(asset)
                self.db.flush()

                # Create AccessRelationship
                rel = AccessRelationship(
                    organization_id=self.org_id,
                    application_instance_id=instance.id,
                    data_asset_id=asset.id,
                    access_type="READ" if "read" in [p.raw_provider_value for p in installation.permissions] else "WRITE",
                    is_direct=True,
                    last_verified_at=datetime.now(timezone.utc),
                )
                self.db.add(rel)

        self.db.flush()
        return instance

    @staticmethod
    def _permission_risk_weight(severity: str) -> float:
        return {"CRITICAL": 0.9, "HIGH": 0.7, "MEDIUM": 0.5, "LOW": 0.3, "INFO": 0.1}.get(severity, 0.5)

    # ------------------------------------------------------------------
    # Stage 4+5: Risk Engine + Snapshot
    # ------------------------------------------------------------------

    def run_risk_and_snapshot(self, instance: ApplicationInstance, sync_run: ConnectorSyncRun) -> int:
        """
        Run the existing deterministic RiskEngine (v1.5.0) against the live-discovered instance.
        Then create a SecuritySnapshot. Returns count of findings created.
        The frozen risk engine is NOT modified — same engine handles demo + live data.
        """
        # SnapshotEngine takes (db, organization_id)
        try:
            # Find previous trusted snapshot for comparison
            prev_snapshot = self.db.query(SecuritySnapshot).filter(
                SecuritySnapshot.organization_id == self.org_id
            ).order_by(SecuritySnapshot.created_at.desc()).first()
            prev_snapshot_id = prev_snapshot.id if prev_snapshot else None

            snapshot_engine = SnapshotEngine(self.db, self.org_id)
            snapshot = snapshot_engine.create_snapshot(
                label=f"GitHub Live Sync — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC",
                trigger_reason=f"CONNECTOR_SYNC:{self.connector_id}",
            )
            if sync_run and snapshot:
                sync_run.snapshot_id = snapshot.id
            self.db.flush()

            # Execute SecurityDiffEngine to detect continuous monitoring changes
            if snapshot:
                diff_engine = SecurityDiffEngine(self.db, self.org_id)
                diff_engine.compare_snapshots(prev_snapshot_id, snapshot.id)

        except Exception as e:
            logger.warning("Snapshot creation or diff engine failed: %s", e)

        findings_count = len(instance.findings) if hasattr(instance, "findings") else 0
        return findings_count

    # ------------------------------------------------------------------
    # Full Pipeline
    # ------------------------------------------------------------------

    def process_installation(self, installation: NormalizedInstallation,
                              raw_payload: dict, evidence_hash: str,
                              sync_run: ConnectorSyncRun) -> dict:
        """Process one installation through the full pipeline. Isolated — failures don't cascade."""
        result = {
            "installation_id": installation.installation_id,
            "evidence_id": None,
            "facts_count": 0,
            "instance_id": None,
            "findings_count": 0,
            "errors": [],
        }
        try:
            evidence = self.capture_evidence(raw_payload, evidence_hash,
                                              f"installation_{installation.installation_id}")
            result["evidence_id"] = evidence.id
        except Exception as e:
            result["errors"].append(f"Evidence capture failed: {e}")
            return result

        try:
            facts = self.create_security_facts(installation, evidence)
            result["facts_count"] = len(facts)
        except Exception as e:
            result["errors"].append(f"Security facts failed: {e}")

        try:
            instance = self.map_to_domain(installation, evidence)
            if instance:
                result["instance_id"] = instance.id
                findings_count = self.run_risk_and_snapshot(instance, sync_run)
                result["findings_count"] = findings_count
        except Exception as e:
            result["errors"].append(f"Domain mapping failed: {e}")

        return result
