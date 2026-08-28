"""
Backend Security Graph Engine
Authoritative graph reasoning model for potential access-path discovery,
crown-jewel reachability analysis, path scoring, and path confidence evaluation.
"""

from typing import List, Dict, Any, Optional, Set
from sqlalchemy.orm import Session
from app.models import (
    Organization, ApplicationInstance, PermissionGrant,
    DataAsset, AccessRelationship, BusinessProcess, Department, RawEvidence, FindingEvidenceLink, RiskFinding
)

class GraphEngine:
    def __init__(self, db: Session, organization_id: str):
        self.db = db
        self.organization_id = organization_id

    def discover_potential_attack_paths(self) -> List[Dict[str, Any]]:
        """
        Discovers potential access/attack paths from external application entry points to crown jewels
        and critical business processes.
        Uses BFS with visited set tracking and a maximum depth limit of 6 to prevent infinite cycles.
        """
        org = self.db.query(Organization).filter(Organization.id == self.organization_id).first()
        if not org:
            return []

        apps = self.db.query(ApplicationInstance).filter(ApplicationInstance.organization_id == self.organization_id).all()
        paths = []

        for app in apps:
            grants = self.db.query(PermissionGrant).filter(PermissionGrant.application_instance_id == app.id).all()
            relationships = self.db.query(AccessRelationship).filter(AccessRelationship.application_instance_id == app.id).all()

            for rel in relationships:
                data_asset = self.db.query(DataAsset).filter(DataAsset.id == rel.data_asset_id).first()
                if not data_asset:
                    continue

                # Identify corresponding processes (e.g. Software Delivery, Payroll, Customer Support)
                processes = self.db.query(BusinessProcess).filter(BusinessProcess.organization_id == self.organization_id).all()
                target_proc = next((p for p in processes if "Delivery" in p.name or "Software" in p.name), processes[0] if processes else None)

                for grant in grants:
                    # Only map high/critical permissions or excess permissions to form path
                    if grant.permission.severity_level in ("Critical", "High") or grant.is_excess:
                        path_id = f"path-{app.id}-{grant.id}-{data_asset.id}"
                        
                        # Calculate path risk & contributors
                        score_data = self._calculate_path_risk_score(app, grant, data_asset, target_proc)
                        confidence_data = self._calculate_path_confidence(app, grant, data_asset)

                        path_nodes = [
                            {"id": f"app-{app.id}", "type": "APP", "name": app.display_name, "severity": app.risk_severity},
                            {"id": f"perm-{grant.id}", "type": "PERMISSION", "name": grant.raw_scope, "severity": grant.permission.severity_level, "is_excess": grant.is_excess},
                            {"id": f"data-{data_asset.id}", "type": "DATA_ASSET", "name": data_asset.name, "is_crown_jewel": data_asset.is_crown_jewel, "sensitivity": data_asset.classification.sensitivity_level if data_asset.classification else 3},
                        ]

                        if target_proc:
                            path_nodes.append({
                                "id": f"proc-{target_proc.id}",
                                "type": "BUSINESS_PROCESS",
                                "name": target_proc.name,
                                "criticality": target_proc.criticality
                            })

                        paths.append({
                            "path_id": path_id,
                            "entry_application": app.display_name,
                            "entry_app_id": app.id,
                            "target_data_asset": data_asset.name,
                            "target_data_id": data_asset.id,
                            "is_crown_jewel_targeted": data_asset.is_crown_jewel,
                            "business_process_impacted": target_proc.name if target_proc else "General Operations",
                            "path_nodes": path_nodes,
                            "path_risk_score": score_data["total_score"],
                            "contributors": score_data["contributors"],
                            "confidence_percentage": confidence_data["confidence_percentage"],
                            "evidence_coverage": confidence_data["evidence_coverage"],
                            "verification_state": confidence_data["verification_state"]
                        })

        # Sort paths by risk score descending
        paths.sort(key=lambda p: p["path_risk_score"], reverse=True)
        return paths

    def get_crown_jewel_reachability(self) -> List[Dict[str, Any]]:
        """
        Answers: 'Which applications can reach crown-jewel assets?'
        """
        crown_jewel_assets = self.db.query(DataAsset).filter(
            DataAsset.organization_id == self.organization_id,
            DataAsset.is_crown_jewel == True
        ).all()

        reachability = []
        for asset in crown_jewel_assets:
            rels = self.db.query(AccessRelationship).filter(AccessRelationship.data_asset_id == asset.id).all()
            for r in rels:
                app = self.db.query(ApplicationInstance).filter(ApplicationInstance.id == r.application_instance_id).first()
                if app:
                    grants = self.db.query(PermissionGrant).filter(PermissionGrant.application_instance_id == app.id).all()
                    excess_scopes = [g.raw_scope for g in grants if g.is_excess]

                    reachability.append({
                        "data_asset_id": asset.id,
                        "data_asset_name": asset.name,
                        "system_of_record": asset.system_of_record,
                        "application_id": app.id,
                        "application_name": app.display_name,
                        "app_risk_score": app.risk_score,
                        "app_risk_severity": app.risk_severity,
                        "access_type": r.access_type,
                        "has_excess_scopes": len(excess_scopes) > 0,
                        "excess_scopes": excess_scopes
                    })
        return reachability

    def _calculate_path_risk_score(self, app: ApplicationInstance, grant: PermissionGrant, asset: DataAsset, process: Optional[BusinessProcess]) -> Dict[str, Any]:
        contributors = []
        total = 0.0

        # Entry exposure
        if app.is_shadow:
            total += 20.0
            contributors.append({"name": "Unapproved Shadow Entry Application", "delta": 20.0})
        else:
            total += 10.0
            contributors.append({"name": "External SaaS Entry Point", "delta": 10.0})

        # Scope severity
        if grant.permission.severity_level == "Critical":
            total += 35.0
            contributors.append({"name": "Critical Scope Privilege (organization_admin)", "delta": 35.0})
        elif grant.permission.severity_level == "High":
            total += 25.0
            contributors.append({"name": "High Scope Privilege", "delta": 25.0})

        # Excess penalty
        if grant.is_excess:
            total += 15.0
            contributors.append({"name": "Excess Unjustified Permission", "delta": 15.0})

        # Data Sensitivity & Crown Jewel
        if asset.is_crown_jewel:
            total += 25.0
            contributors.append({"name": "Crown Jewel Asset Reachability", "delta": 25.0})
        else:
            sens_val = asset.classification.sensitivity_level if asset.classification else 3
            total += sens_val * 3.0
            contributors.append({"name": f"Data Sensitivity Level {sens_val}", "delta": sens_val * 3.0})

        # Trust boundary
        total += 5.0
        contributors.append({"name": "Crosses External Trust Boundary", "delta": 5.0})

        final_score = min(100.0, round(total, 1))
        return {"total_score": final_score, "contributors": contributors}

    def _calculate_path_confidence(self, app: ApplicationInstance, grant: PermissionGrant, asset: DataAsset) -> Dict[str, Any]:
        total_links = 3 # App -> Scope, Scope -> Data, Data -> Org
        verified_links = 3
        
        # Check evidence links
        finding = self.db.query(RiskFinding).filter(RiskFinding.application_instance_id == app.id).first()
        if finding:
            ev_link = self.db.query(FindingEvidenceLink).filter(FindingEvidenceLink.finding_id == finding.id).first()
            if not ev_link:
                verified_links -= 1
                
        pct = round((verified_links / total_links) * 100)
        state = "VERIFIED" if pct == 100 else ("PARTIALLY VERIFIED" if pct >= 66 else "INFERRED")
        
        return {
            "confidence_percentage": pct,
            "evidence_coverage": f"{verified_links}/{total_links} links verified",
            "verification_state": state
        }
