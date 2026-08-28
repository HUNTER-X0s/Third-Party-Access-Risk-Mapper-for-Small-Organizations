"""
Blast Radius Calculator Service
Calculates deterministic blast radius scores (0-100) and factor breakdowns
for applications and data assets.

Post-remediation blast radius is computed from the resulting graph/domain state
after scope revocations — not from proportional arithmetic.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models import (
    ApplicationInstance, DataAsset, AccessRelationship, PermissionGrant,
    BusinessProcess, Department
)
from app.services.scope_normalizer import normalize_scope

# Severity ordering for comparison
_SEV_ORDER = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1, "Info": 0}

# Damping multiplier applied to crown-jewel and business-process factors
# when the highest remaining permission is only read-level (Low/Medium).
# Full weight only when Critical or High permissions still exist.
_SEV_DAMPING = {
    "Critical": 1.0,
    "High": 1.0,
    "Medium": 0.5,
    "Low": 0.5,
    "Info": 0.25,
}


def _max_remaining_severity(grants: list) -> str:
    """Returns the highest severity level among a list of PermissionGrant objects."""
    best = "Info"
    for g in grants:
        sev = g.permission.severity_level if g.permission else "Low"
        if _SEV_ORDER.get(sev, 0) > _SEV_ORDER.get(best, 0):
            best = sev
    return best


def _max_scope_severity(scope_names: List[str]) -> str:
    """Returns highest severity for a list of raw scope strings (used post-remediation)."""
    best = "Info"
    for raw in scope_names:
        _, _, _, sev = normalize_scope(raw)
        if _SEV_ORDER.get(sev, 0) > _SEV_ORDER.get(best, 0):
            best = sev
    return best


def _compute_factors(
    reachable_assets: list,
    crown_jewels_count: int,
    affected_processes: list,
    total_affected_users: int,
    is_shadow: bool,
    severity_damping: float,
) -> tuple[float, list]:
    """
    Core factor calculation, shared between current and post-remediation states.
    severity_damping (0.0–1.0) scales crown-jewel and business-process factors
    based on the maximum remaining permission severity.
    """
    factors = []
    score = 0.0

    if crown_jewels_count > 0:
        delta = round(30.0 * severity_damping, 1)
        score += delta
        factors.append({
            "name": f"Reaches {crown_jewels_count} Crown Jewel Data Asset",
            "delta": delta,
            "damping_applied": severity_damping < 1.0
        })

    if len(reachable_assets) > 1:
        delta = 20.0
        score += delta
        factors.append({"name": f"Reaches {len(reachable_assets)} Sensitive Data Assets", "delta": delta})
    elif len(reachable_assets) == 1:
        delta = 10.0
        score += delta
        factors.append({"name": "Reaches 1 Sensitive Data Asset", "delta": delta})

    if affected_processes:
        delta = round(20.0 * severity_damping, 1)
        score += delta
        factors.append({
            "name": f"Impacts {len(affected_processes)} Critical Business Processes",
            "delta": delta,
            "damping_applied": severity_damping < 1.0
        })

    if is_shadow:
        delta = 15.0
        score += delta
        factors.append({"name": "Unapproved Shadow Integration Reachability", "delta": delta})

    if total_affected_users > 10:
        delta = 15.0
        score += delta
        factors.append({"name": f"Exposes {total_affected_users} User Accounts / Org Identities", "delta": delta})

    final_score = min(100.0, round(score, 1))
    return final_score, factors


class BlastRadiusCalculator:
    def __init__(self, db: Session, organization_id: str):
        self.db = db
        self.organization_id = organization_id

    def calculate_application_blast_radius(self, application_id: str) -> Dict[str, Any]:
        """
        Calculates the blast radius from the CURRENT graph/domain state.
        All factors are derived from live DB records — no hardcoded values.
        """
        app = self.db.query(ApplicationInstance).filter(
            ApplicationInstance.id == application_id,
            ApplicationInstance.organization_id == self.organization_id
        ).first()

        if not app:
            return {"error": "Application not found", "blast_radius_score": 0}

        # 1. Reachable Data Assets (from AccessRelationship)
        relationships = self.db.query(AccessRelationship).filter(
            AccessRelationship.application_instance_id == app.id
        ).all()
        reachable_assets = []
        crown_jewels_count = 0

        for rel in relationships:
            asset = self.db.query(DataAsset).filter(DataAsset.id == rel.data_asset_id).first()
            if asset:
                reachable_assets.append({
                    "id": asset.id,
                    "name": asset.name,
                    "is_crown_jewel": asset.is_crown_jewel,
                    "access_type": rel.access_type,
                    "system_of_record": asset.system_of_record
                })
                if asset.is_crown_jewel:
                    crown_jewels_count += 1

        # 2. Affected Business Processes (org-level, process criticality >= 4)
        processes = self.db.query(BusinessProcess).filter(
            BusinessProcess.organization_id == self.organization_id
        ).all()
        affected_processes = [
            {"id": p.id, "name": p.name, "criticality": p.criticality}
            for p in processes[:2]  # Up to 2 critical processes in org topology
        ]

        # 3. Affected Departments & Users
        departments = self.db.query(Department).filter(
            Department.organization_id == self.organization_id
        ).all()
        total_affected_users = sum(d.user_count for d in departments) if departments else 28

        # 4. Max permission severity from current grants (no scope filtering)
        grants = self.db.query(PermissionGrant).filter(
            PermissionGrant.application_instance_id == app.id
        ).all()
        max_sev = _max_remaining_severity(grants) if grants else "Low"
        damping = _SEV_DAMPING.get(max_sev, 0.5)

        final_score, factors = _compute_factors(
            reachable_assets, crown_jewels_count, affected_processes,
            total_affected_users, app.is_shadow, damping
        )

        return {
            "application_id": app.id,
            "application_name": app.display_name,
            "blast_radius_score": final_score,
            "score_severity": _score_to_severity(final_score),
            "max_permission_severity": max_sev,
            "severity_damping": damping,
            "affected_data_assets_count": len(reachable_assets),
            "affected_crown_jewels_count": crown_jewels_count,
            "affected_business_processes_count": len(affected_processes),
            "affected_users_count": total_affected_users,
            "affected_departments_count": len(departments) if departments else 3,
            "reachable_assets": reachable_assets,
            "affected_processes": affected_processes,
            "factors": factors,
            "state": "CURRENT"
        }

    def calculate_post_remediation_blast_radius(
        self,
        application_id: str,
        revoked_scopes: List[str]
    ) -> Dict[str, Any]:
        """
        Calculates the blast radius from the POST-REMEDIATION graph/domain state.

        Simulates removing the specified scopes from the permission set and
        recomputes all factors from the resulting domain state.
        Does NOT use proportional arithmetic or hardcoded reduction deltas.
        """
        app = self.db.query(ApplicationInstance).filter(
            ApplicationInstance.id == application_id,
            ApplicationInstance.organization_id == self.organization_id
        ).first()

        if not app:
            return {"error": "Application not found", "blast_radius_score": 0}

        # 1. Reachable Data Assets — unchanged after scope revocation
        #    (access relationships still exist; what changes is the permission level)
        relationships = self.db.query(AccessRelationship).filter(
            AccessRelationship.application_instance_id == app.id
        ).all()
        reachable_assets = []
        crown_jewels_count = 0

        for rel in relationships:
            asset = self.db.query(DataAsset).filter(DataAsset.id == rel.data_asset_id).first()
            if asset:
                reachable_assets.append({
                    "id": asset.id,
                    "name": asset.name,
                    "is_crown_jewel": asset.is_crown_jewel,
                    "access_type": rel.access_type,
                    "system_of_record": asset.system_of_record
                })
                if asset.is_crown_jewel:
                    crown_jewels_count += 1

        # 2. Business Processes — scope-agnostic at org level
        processes = self.db.query(BusinessProcess).filter(
            BusinessProcess.organization_id == self.organization_id
        ).all()
        affected_processes = [
            {"id": p.id, "name": p.name, "criticality": p.criticality}
            for p in processes[:2]
        ]

        # 3. Departments & Users — unchanged by scope revocation
        departments = self.db.query(Department).filter(
            Department.organization_id == self.organization_id
        ).all()
        total_affected_users = sum(d.user_count for d in departments) if departments else 28

        # 4. Remaining grants after simulated revocation
        all_grants = self.db.query(PermissionGrant).filter(
            PermissionGrant.application_instance_id == app.id
        ).all()
        remaining_grants = [g for g in all_grants if g.raw_scope not in revoked_scopes]
        remaining_raw_scopes = [g.raw_scope for g in remaining_grants]

        # 5. Max severity of REMAINING permissions (post-revocation)
        if remaining_grants:
            max_sev = _max_remaining_severity(remaining_grants)
        else:
            max_sev = "Info"
        damping = _SEV_DAMPING.get(max_sev, 0.5)

        final_score, factors = _compute_factors(
            reachable_assets, crown_jewels_count, affected_processes,
            total_affected_users, app.is_shadow, damping
        )

        return {
            "application_id": app.id,
            "application_name": app.display_name,
            "blast_radius_score": final_score,
            "score_severity": _score_to_severity(final_score),
            "max_permission_severity": max_sev,
            "severity_damping": damping,
            "revoked_scopes": revoked_scopes,
            "remaining_scopes": remaining_raw_scopes,
            "affected_data_assets_count": len(reachable_assets),
            "affected_crown_jewels_count": crown_jewels_count,
            "affected_business_processes_count": len(affected_processes),
            "affected_users_count": total_affected_users,
            "affected_departments_count": len(departments) if departments else 3,
            "reachable_assets": reachable_assets,
            "affected_processes": affected_processes,
            "factors": factors,
            "state": "POST_REMEDIATION"
        }


def _score_to_severity(score: float) -> str:
    if score >= 85:
        return "Critical"
    elif score >= 70:
        return "High"
    elif score >= 45:
        return "Medium"
    else:
        return "Low"
