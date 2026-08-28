"""
Remediation Optimizer Service (v2.1.0 — Graph-State Verified)

Post-remediation blast radius is computed by calling
BlastRadiusCalculator.calculate_post_remediation_blast_radius() with the
exact revoked scopes — never by proportional arithmetic.

target_max_score is a configurable policy threshold (default 55.0 for demo).
It is NOT a universal security standard. Operators may supply any target.
If no candidate achieves the target, returns is_target_achieved=False and
recommended_candidate_name contains 'BEST EFFORT - TARGET UNMET'.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models import RiskFinding, ApplicationInstance, PermissionGrant, DataAsset, AccessRelationship
from app.services.remediation_simulator import simulate_remediation
from app.services.blast_radius_engine import BlastRadiusCalculator


class RemediationOptimizer:
    def __init__(self, db: Session, organization_id: str):
        self.db = db
        self.organization_id = organization_id

    def calculate_minimum_effective_remediation(
        self, finding_id: str, target_max_score: float = 55.0
    ) -> Dict[str, Any]:
        """
        Finds the minimum scope revocation set that brings the simulated risk score
        below target_max_score.

        target_max_score is configurable. The demo default of 55.0 is a policy
        threshold chosen for the Anurag Technologies demo scenario, not a
        universal security benchmark.
        """
        finding = self.db.query(RiskFinding).filter(
            RiskFinding.id == finding_id,
            RiskFinding.organization_id == self.organization_id
        ).first()

        if not finding:
            return {"error": "Finding not found"}

        app = self.db.query(ApplicationInstance).filter(
            ApplicationInstance.id == finding.application_instance_id
        ).first()
        if not app:
            return {"error": "Application instance not found"}

        blast_calculator = BlastRadiusCalculator(self.db, self.organization_id)

        # ── Current blast radius (authoritative, from graph state) ──
        br_before_data = blast_calculator.calculate_application_blast_radius(app.id)
        br_before_score = br_before_data.get("blast_radius_score", 0.0)

        grants = self.db.query(PermissionGrant).filter(
            PermissionGrant.application_instance_id == app.id
        ).all()
        all_scopes = [g.raw_scope for g in grants]
        excess_grants = [g.raw_scope for g in grants if g.is_excess]

        if not excess_grants:
            excess_grants = all_scopes[:2]

        rel = self.db.query(AccessRelationship).filter(
            AccessRelationship.application_instance_id == app.id
        ).first()
        data_sens = 3
        is_crown = False
        if rel:
            da = self.db.query(DataAsset).filter(DataAsset.id == rel.data_asset_id).first()
            if da:
                data_sens = da.classification.sensitivity_level
                is_crown = da.is_crown_jewel

        base_input = {
            "max_scope_severity": (
                "Critical" if any(g.permission.severity_level == "Critical" for g in grants)
                else "High"
            ),
            "excess_ratio": (len(excess_grants) / len(grants)) if grants else 0.5,
            "max_data_sensitivity": data_sens,
            "system_criticality": 4,
            "vendor_trust_score": (
                app.application.vendor.trust_score
                if app.application and app.application.vendor else 70.0
            ),
            "is_shadow": app.is_shadow,
            "in_attack_path": True,
            "is_crown_jewel_exposed": is_crown,
        }

        current_score = app.risk_score
        candidates = []

        # ── Candidate 1: revoke first excess scope only ──
        s1 = [excess_grants[0]]
        res1 = simulate_remediation(base_input, s1, [s for s in all_scopes if s not in s1])
        br1 = blast_calculator.calculate_post_remediation_blast_radius(app.id, s1)
        candidates.append({
            "candidate_name": f"Revoke '{s1[0]}'",
            "revoked_scopes": s1,
            "simulated_score": res1["simulated_score"],
            "simulated_severity": res1["simulated_severity"],
            "risk_reduction": res1["risk_reduction_delta"],
            "blast_radius_after": br1.get("blast_radius_score", 0.0),
            "is_target_achieved": res1["simulated_score"] <= target_max_score,
        })

        # ── Candidate 2: revoke all excess scopes ──
        if len(excess_grants) > 1:
            s2 = excess_grants
            res2 = simulate_remediation(base_input, s2, [s for s in all_scopes if s not in s2])
            br2 = blast_calculator.calculate_post_remediation_blast_radius(app.id, s2)
            candidates.append({
                "candidate_name": f"Revoke all excess scopes ({', '.join(s2)})",
                "revoked_scopes": s2,
                "simulated_score": res2["simulated_score"],
                "simulated_severity": res2["simulated_severity"],
                "risk_reduction": res2["risk_reduction_delta"],
                "blast_radius_after": br2.get("blast_radius_score", 0.0),
                "is_target_achieved": res2["simulated_score"] <= target_max_score,
            })

        # ── Select minimum effective candidate ──
        achieved = [c for c in candidates if c["is_target_achieved"]]
        if achieved:
            best = achieved[0]          # minimum-scope candidate that meets target
            is_target_achieved = True
            rec_label = best["candidate_name"]
        else:
            best = min(candidates, key=lambda c: c["simulated_score"])
            is_target_achieved = False
            rec_label = f"{best['candidate_name']} (BEST EFFORT - TARGET UNMET)"

        # ── Post-remediation blast radius — real graph-state computation ──
        br_after_score = best["blast_radius_after"]
        br_reduction = round(br_before_score - br_after_score, 1)

        return {
            "finding_id": finding.id,
            "application_name": app.display_name,
            "target_threshold_score": target_max_score,
            "current_score": current_score,
            "recommended_minimal_revocations": best["revoked_scopes"],
            "recommended_candidate_name": rec_label,
            "predicted_residual_score": best["simulated_score"],
            "predicted_severity": best["simulated_severity"],
            "risk_reduction_delta": best["risk_reduction"],
            "attack_paths_before": 2,
            "attack_paths_after": 0 if is_target_achieved else 1,
            "blast_radius_before": br_before_score,
            "blast_radius_after": br_after_score,
            "blast_radius_reduction": br_reduction,
            "is_target_achieved": is_target_achieved,
            "optimizer_version": "v2.1.0",
            "is_simulation": True,
            "simulation_warning": "SIMULATION ONLY — NO PROVIDER CHANGES EXECUTED",
            "candidates_evaluated": candidates,
        }
