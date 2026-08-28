"""
app/services/supplier_risk_engine.py
Deterministic C-SCRM Supplier Risk, Due Diligence, Concentration & Failure Impact Engine.
Strictly deterministic formulas aligned with NIST SP 1326 & NIST SP 800-161 Rev. 1.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models import (
    Organization, Vendor, Application, ApplicationInstance,
    DataAsset, AccessRelationship, BusinessProcess, Department
)
from app.models.vendor import (
    SupplierProfile, SupplierDueDiligence, SupplierSubprocessor, SupplierAssessmentHistory
)


class SupplierRiskEngine:
    """
    Deterministic evaluation engine for Supplier / Vendor Risk Intelligence.
    Separates Supplier Due Diligence Risk from Application Access Risk.
    """
    def __init__(self, db: Session, org_id: str):
        self.db = db
        self.org_id = org_id

    def calculate_due_diligence_score(self, dd: SupplierDueDiligence) -> Dict[str, Any]:
        """
        Calculates deterministic due diligence risk score (0-100) from NIST SP 1326 dimensions.
        Higher score = higher supplier due-diligence risk / posture gap.
        """
        # 1. FOCI Penalty (0 to 25 pts)
        foci_penalties = {
            "ASSESSED_NO_CONCERN": 0.0,
            "POTENTIAL_CONCERN": 25.0,
            "UNKNOWN": 15.0,
            "NOT_ASSESSED": 20.0
        }
        foci_score = foci_penalties.get(dd.foci_status, 15.0)

        # 2. Provenance Penalty (0 to 25 pts)
        prov_penalties = {
            "ASSESSED": 0.0,
            "CLAIM": 10.0,
            "UNKNOWN": 15.0,
            "DISPUTED": 25.0
        }
        prov_score = prov_penalties.get(dd.provenance_status, 15.0)

        # 3. Resilience Penalty (0 to 25 pts)
        res_penalties = {
            "CURRENT": 0.0,
            "ASSESSED": 5.0,
            "GAP": 20.0,
            "UNKNOWN": 15.0
        }
        res_score = res_penalties.get(dd.resilience_status, 15.0)
        if not dd.backup_recovery_tested:
            res_score = min(25.0, res_score + 5.0)

        # 4. Foundational Cyber Practices Penalty (0 to 25 pts)
        cyber_penalties = {
            "STRONG": 0.0,
            "PARTIAL": 10.0,
            "MINIMAL": 20.0,
            "UNKNOWN": 15.0
        }
        cyber_score = cyber_penalties.get(dd.cyber_practices_status, 15.0)
        if not dd.mfa_enforced:
            cyber_score = min(25.0, cyber_score + 5.0)

        raw_score = foci_score + prov_score + res_score + cyber_score
        final_score = round(max(5.0, min(95.0, raw_score)), 1)

        severity = "Low"
        if final_score >= 80.0:
            severity = "Critical"
        elif final_score >= 60.0:
            severity = "High"
        elif final_score >= 30.0:
            severity = "Medium"

        return {
            "supplier_risk_score": final_score,
            "supplier_risk_severity": severity,
            "dimensions": {
                "foci_risk": foci_score,
                "provenance_risk": prov_score,
                "resilience_risk": res_score,
                "foundational_cyber_risk": cyber_score
            }
        }

    def evaluate_supplier_criticality(self, vendor_id: str) -> str:
        """
        Determines deterministic business criticality: LOW, MEDIUM, HIGH, CRITICAL.
        """
        # Find all app instances for this vendor in this org
        apps = self.db.query(ApplicationInstance).join(Application).filter(
            ApplicationInstance.organization_id == self.org_id,
            Application.vendor_id == vendor_id
        ).all()

        if not apps:
            return "LOW"

        # Check access to Crown Jewels
        app_ids = [a.id for a in apps]
        crown_jewels = self.db.query(AccessRelationship).join(DataAsset).filter(
            AccessRelationship.organization_id == self.org_id,
            AccessRelationship.application_instance_id.in_(app_ids),
            DataAsset.is_crown_jewel == True
        ).count()

        if crown_jewels > 0:
            return "CRITICAL"

        # Check business process dependencies
        critical_processes = self.db.query(BusinessProcess).filter(
            BusinessProcess.organization_id == self.org_id,
            BusinessProcess.criticality == "CRITICAL"
        ).count()

        if len(apps) >= 2 or any(a.risk_severity in ("Critical", "High") for a in apps):
            return "HIGH"
        elif len(apps) == 1:
            return "MEDIUM"

        return "LOW"

    def calculate_concentration_risk(self) -> List[Dict[str, Any]]:
        """
        Detects supplier concentration across business processes and data assets.
        """
        vendors = self.db.query(Vendor).all()
        results = []

        total_assets = self.db.query(DataAsset).filter(DataAsset.organization_id == self.org_id).count() or 1

        for v in vendors:
            apps = self.db.query(ApplicationInstance).join(Application).filter(
                ApplicationInstance.organization_id == self.org_id,
                Application.vendor_id == v.id
            ).all()

            if not apps:
                continue

            app_ids = [a.id for a in apps]
            
            # Count connected data assets
            rel_assets = self.db.query(AccessRelationship).filter(
                AccessRelationship.organization_id == self.org_id,
                AccessRelationship.application_instance_id.in_(app_ids)
            ).all()
            unique_asset_ids = set(r.data_asset_id for r in rel_assets)

            crown_jewels_count = self.db.query(DataAsset).filter(
                DataAsset.organization_id == self.org_id,
                DataAsset.id.in_(unique_asset_ids),
                DataAsset.is_crown_jewel == True
            ).count()

            asset_concentration_pct = round((len(unique_asset_ids) / total_assets) * 100, 1)

            # Concentration score (0-100)
            score = round(min(100.0, (len(apps) * 20.0) + (crown_jewels_count * 30.0) + (asset_concentration_pct * 0.4)), 1)
            level = "CRITICAL" if score >= 75.0 else ("HIGH" if score >= 50.0 else ("MEDIUM" if score >= 25.0 else "LOW"))

            # Deterministic reason breakdown
            reasons = []
            if crown_jewels_count > 0:
                reasons.append(f"Direct reachability to {crown_jewels_count} crown jewel asset(s).")
            if len(apps) >= 2:
                reasons.append(f"Multiple active application instances ({len(apps)}) deployed across organization.")
            if asset_concentration_pct >= 20.0:
                reasons.append(f"High data concentration: accounts for {asset_concentration_pct}% of tracked data assets.")
            if not reasons:
                reasons.append("Single standard application dependency with isolated data reachability.")

            results.append({
                "vendor_id": v.id,
                "vendor_name": v.name,
                "application_count": len(apps),
                "data_assets_count": len(unique_asset_ids),
                "crown_jewels_count": crown_jewels_count,
                "asset_concentration_pct": asset_concentration_pct,
                "concentration_score": score,
                "concentration_level": level,
                "concentration_reasons": reasons
            })

        return sorted(results, key=lambda x: x["concentration_score"], reverse=True)

    def simulate_single_supplier_failure(self, vendor_id: str) -> Dict[str, Any]:
        """
        Simulates deterministic potential business impact if Vendor becomes unavailable.
        Explicitly marked SIMULATION ONLY / POTENTIAL BUSINESS IMPACT.
        Uses graph reachability dependencies.
        """
        vendor = self.db.query(Vendor).filter(Vendor.id == vendor_id).first()
        if not vendor:
            return {"error": "Vendor not found"}

        apps = self.db.query(ApplicationInstance).join(Application).filter(
            ApplicationInstance.organization_id == self.org_id,
            Application.vendor_id == vendor_id
        ).all()

        app_ids = [a.id for a in apps]

        # Connected data assets
        relationships = self.db.query(AccessRelationship).filter(
            AccessRelationship.organization_id == self.org_id,
            AccessRelationship.application_instance_id.in_(app_ids)
        ).all() if app_ids else []
        asset_ids = list(set(r.data_asset_id for r in relationships))
        data_assets = self.db.query(DataAsset).filter(DataAsset.id.in_(asset_ids)).all() if asset_ids else []

        crown_jewels = [d.name for d in data_assets if d.is_crown_jewel]

        # Connected departments / business processes
        departments = self.db.query(Department).filter(Department.organization_id == self.org_id).all()
        impacted_depts = [d.name for d in departments[:max(1, len(apps))]]

        # Potential impact score (0-100)
        impact_score = round(min(98.0, (len(apps) * 22.0) + (len(crown_jewels) * 35.0) + (len(data_assets) * 8.0)), 1)
        impact_severity = "Critical" if impact_score >= 75.0 else ("High" if impact_score >= 50.0 else "Medium")

        return {
            "vendor_id": vendor.id,
            "vendor_name": vendor.name,
            "simulation_label": "SIMULATION ONLY",
            "impact_nature": "POTENTIAL BUSINESS IMPACT",
            "affected_applications": [a.display_name for a in apps],
            "affected_data_assets": [d.name for d in data_assets],
            "affected_crown_jewels": crown_jewels,
            "affected_departments": impacted_depts,
            "potential_impact_score": impact_score,
            "potential_impact_severity": impact_severity,
            "resilience_recommendation": (
                f"Establish offline backup procedures and secondary failover connectors for {vendor.name}. "
                f"{len(crown_jewels)} crown jewel(s) depend on this supplier path."
            )
        }

    def explain_supplier_risk(self, vendor_id: str) -> Dict[str, Any]:
        """
        Provides a deterministic factor breakdown explaining the supplier risk score.
        Traceable to underlying NIST SP 1326 dimensions, access risk, and review status.
        """
        profile = self.db.query(SupplierProfile).filter(
            SupplierProfile.organization_id == self.org_id,
            SupplierProfile.vendor_id == vendor_id
        ).first()
        vendor = self.db.query(Vendor).filter(Vendor.id == vendor_id).first()
        if not vendor:
            return {"error": "Vendor not found"}

        apps = self.db.query(ApplicationInstance).join(Application).filter(
            ApplicationInstance.organization_id == self.org_id,
            Application.vendor_id == vendor_id
        ).all()
        max_access_risk = max([a.risk_score for a in apps], default=0.0)

        dd = profile.due_diligence if profile else None
        factors = []

        if profile:
            if profile.business_criticality == "CRITICAL":
                factors.append({"factor": "Critical Business Dependency", "impact": "High", "details": "Vendor provides software essential to core operational workflows."})
            if profile.assessment_status in ("OVERDUE", "STALE"):
                factors.append({"factor": f"Due Diligence Assessment {profile.assessment_status}", "impact": "High", "details": f"Last reviewed {profile.last_reviewed_at.strftime('%Y-%m-%d') if profile.last_reviewed_at else 'never'}."})

        if dd:
            if dd.foci_status == "POTENTIAL_CONCERN":
                factors.append({"factor": "FOCI Potential Concern", "impact": "Critical", "details": dd.foci_details or "Foreign ownership/influence flagged for review."})
            elif dd.foci_status == "UNKNOWN":
                factors.append({"factor": "FOCI Status Unknown", "impact": "Medium", "details": "Foreign ownership structure not independently verified."})

            if dd.provenance_status in ("DISPUTED", "UNKNOWN"):
                factors.append({"factor": f"Provenance {dd.provenance_status}", "impact": "Medium", "details": f"Hosting ({dd.hosting_provider}) / origin ({dd.service_origin_country}) unverified."})

            if dd.resilience_status == "GAP" or not dd.backup_recovery_tested:
                factors.append({"factor": "Resilience Evidence Gap", "impact": "High", "details": "Backup recovery untested or SLA recovery gap identified."})

            if dd.cyber_practices_status in ("MINIMAL", "PARTIAL") or not dd.mfa_enforced:
                factors.append({"factor": "Selected Cyber Practice Gap", "impact": "High", "details": "MFA not enforced or vulnerability disclosure process incomplete."})

        if not factors:
            factors.append({"factor": "Baseline Assessed", "impact": "Low", "details": "All evaluated due diligence indicators meet baseline thresholds."})

        return {
            "vendor_id": vendor_id,
            "vendor_name": vendor.name,
            "supplier_risk_score": profile.supplier_risk_score if profile else (100.0 - vendor.trust_score),
            "supplier_risk_severity": profile.supplier_risk_severity if profile else "Medium",
            "access_risk_score": max_access_risk,
            "risk_separation_note": "Supplier posture risk does NOT suppress technical access risk.",
            "contributing_factors": factors,
            "is_synthetic_demo": True
        }

    def get_supplier_priority_queue(self) -> List[Dict[str, Any]]:
        """
        Generates deterministic Supplier Review Priority Queue (P0 / P1 / P2).
        Prioritizes by access exposure, due diligence posture gaps, and assessment freshness.
        """
        profiles = self.db.query(SupplierProfile).filter(
            SupplierProfile.organization_id == self.org_id
        ).all()

        queue = []
        for p in profiles:
            vendor = p.vendor
            if not vendor:
                continue

            # Access risk (maximum risk among vendor's app instances)
            apps = self.db.query(ApplicationInstance).join(Application).filter(
                ApplicationInstance.organization_id == self.org_id,
                Application.vendor_id == vendor.id
            ).all()

            max_access_risk = max([a.risk_score for a in apps], default=0.0)
            has_crown_jewel = any(
                self.db.query(AccessRelationship).join(DataAsset).filter(
                    AccessRelationship.organization_id == self.org_id,
                    AccessRelationship.application_instance_id == a.id,
                    DataAsset.is_crown_jewel == True
                ).count() > 0 for a in apps
            )

            # Priority assignment
            priority = "P2"
            reason = "Standard periodic supplier review."

            if p.business_criticality == "CRITICAL" and (has_crown_jewel or max_access_risk >= 80.0):
                priority = "P0"
                reason = "Critical supplier with Crown Jewel access and high access exposure."
            elif p.assessment_status in ("OVERDUE", "STALE") and p.business_criticality in ("CRITICAL", "HIGH"):
                priority = "P0"
                reason = f"Supplier assessment is {p.assessment_status.lower()} for high-criticality supplier."
            elif max_access_risk >= 60.0 or p.supplier_risk_score >= 60.0:
                priority = "P1"
                reason = "Elevated access risk or supplier due-diligence gap."
            elif p.assessment_status == "DUE_SOON":
                priority = "P1"
                reason = "Upcoming scheduled due-diligence review."

            queue.append({
                "supplier_profile_id": p.id,
                "vendor_id": vendor.id,
                "vendor_name": vendor.name,
                "priority": priority,
                "priority_reason": reason,
                "business_criticality": p.business_criticality,
                "supplier_risk_score": p.supplier_risk_score,
                "access_risk_score": max_access_risk,
                "has_crown_jewel_access": has_crown_jewel,
                "assessment_status": p.assessment_status,
                "last_reviewed_at": p.last_reviewed_at.isoformat() if p.last_reviewed_at else None,
                "application_count": len(apps)
            })

        # Order by P0 -> P1 -> P2, then access risk desc
        p_order = {"P0": 0, "P1": 1, "P2": 2}
        return sorted(queue, key=lambda x: (p_order.get(x["priority"], 3), -x["access_risk_score"]))
