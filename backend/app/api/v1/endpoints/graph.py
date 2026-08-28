from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Organization, ApplicationInstance, DataAsset, AccessRelationship, User, SecurityChange
from app.services.graph_engine import GraphEngine
from app.services.blast_radius_engine import BlastRadiusCalculator
from app.api.deps import get_current_user, get_current_org_id

router = APIRouter()

@router.get("")
def get_access_graph(
    current_user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    """
    Returns Access Graph topology scoped strictly to authenticated user's organization.
    """
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        return {"nodes": [], "edges": []}

    apps = db.query(ApplicationInstance).filter(ApplicationInstance.organization_id == org.id).all()
    data_assets = db.query(DataAsset).filter(DataAsset.organization_id == org.id).all()
    relationships = db.query(AccessRelationship).filter(AccessRelationship.organization_id == org.id).all()

    nodes = []
    edges = []

    nodes.append({
        "id": f"org-{org.id}",
        "type": "organization",
        "data": {
            "label": org.name,
            "domain": org.domain,
            "posture_score": org.security_posture_score
        },
        "position": {"x": 350, "y": 50}
    })

    for idx, app in enumerate(apps):
        node_id = f"app-{app.id}"
        nodes.append({
            "id": node_id,
            "type": "application",
            "data": {
                "label": app.display_name,
                "category": app.application.category if app.application else "General",
                "risk_score": app.risk_score,
                "risk_severity": app.risk_severity,
                "is_shadow": app.is_shadow,
                "status": app.status
            },
            "position": {"x": 50 + (idx * 160) % 800, "y": 200 + (idx // 5) * 120}
        })

        edges.append({
            "id": f"edge-org-{app.id}",
            "source": f"org-{org.id}",
            "target": node_id,
            "animated": app.is_shadow or app.risk_severity == "Critical",
            "style": {"stroke": "#f87171" if app.risk_severity == "Critical" else "#64748b"}
        })

    for idx, asset in enumerate(data_assets):
        node_id = f"data-{asset.id}"
        nodes.append({
            "id": node_id,
            "type": "data_asset",
            "data": {
                "label": asset.name,
                "system": asset.system_of_record,
                "classification": asset.classification.name if asset.classification else "GENERAL",
                "sensitivity": asset.classification.sensitivity_level if asset.classification else 3,
                "is_crown_jewel": asset.is_crown_jewel
            },
            "position": {"x": 100 + (idx * 220), "y": 500}
        })

    for rel in relationships:
        edges.append({
            "id": f"edge-rel-{rel.id}",
            "source": f"app-{rel.application_instance_id}",
            "target": f"data-{rel.data_asset_id}",
            "label": rel.access_type,
            "animated": rel.access_type in ("ADMIN", "EXPORT"),
            "style": {
                "stroke": "#ef4444" if rel.access_type in ("ADMIN", "EXPORT") else "#3b82f6",
                "strokeWidth": 2
            }
        })

    return {
        "organization": org.name,
        "nodes": nodes,
        "edges": edges
    }

@router.get("/delta")
def get_access_graph_delta(
    current_user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    """
    Returns Access Graph topology annotated with change delta states:
    NEW, REMOVED, CHANGED, UNCHANGED.
    """
    base_graph = get_access_graph(current_user=current_user, org_id=org_id, db=db)
    
    # Retrieve recent security changes for this organization
    changes = db.query(SecurityChange).filter(
        SecurityChange.organization_id == org_id
    ).order_by(SecurityChange.timestamp.desc()).limit(50).all()

    # Index changes by object_id / entity name
    escalated_scopes = {c.object_id: c for c in changes if c.change_type == "PERMISSION_ESCALATED"}
    reachability_created = [c for c in changes if c.change_type in ("CROWN_JEWEL_REACHABILITY_CREATED", "NEW_POTENTIAL_ATTACK_PATH")]
    shadow_detected = {c.object_id: c for c in changes if c.change_type == "SHADOW_SAAS_DETECTED"}

    annotated_edges = []
    for edge in base_graph.get("edges", []):
        edge_id = edge["id"]
        source = edge["source"]
        target = edge["target"]
        label = edge.get("label", "")

        status = "UNCHANGED"
        change_meta = None

        # Check if edge is to/from an application involved in changes
        if reachability_created and (label in ("ADMIN", "EXPORT") or "data-" in target):
            # Check if this edge is an escalated admin reachability edge
            rel_change = reachability_created[0]
            status = "CHANGED" if label == "ADMIN" else "NEW"
            change_meta = {
                "change_id": rel_change.id,
                "change_type": rel_change.change_type,
                "severity": rel_change.severity,
                "before": "READ (Limited)",
                "after": f"{label} (Escalated)",
                "risk_impact": rel_change.impact_summary,
                "evidence_refs": rel_change.evidence_refs or []
            }
        elif any(app_id in source for app_id in shadow_detected):
            status = "NEW"
            sh_change = list(shadow_detected.values())[0]
            change_meta = {
                "change_id": sh_change.id,
                "change_type": "SHADOW_SAAS_DETECTED",
                "severity": sh_change.severity,
                "before": "Unobserved",
                "after": "Active (Unapproved)",
                "risk_impact": sh_change.impact_summary,
                "evidence_refs": sh_change.evidence_refs or []
            }

        # Set styling per status
        stroke_color = "#64748b" # UNCHANGED default
        if status == "NEW":
            stroke_color = "#10b981" # Emerald
        elif status == "CHANGED":
            stroke_color = "#f59e0b" # Amber
        elif status == "REMOVED":
            stroke_color = "#ef4444" # Red

        annotated_edges.append({
            **edge,
            "change_status": status,
            "change_metadata": change_meta,
            "style": {
                **edge.get("style", {}),
                "stroke": stroke_color,
                "strokeWidth": 3 if status in ("NEW", "CHANGED") else 1.5
            }
        })

    return {
        "organization": base_graph.get("organization"),
        "nodes": base_graph.get("nodes", []),
        "edges": annotated_edges,
        "delta_summary": {
            "new_edges_count": sum(1 for e in annotated_edges if e["change_status"] == "NEW"),
            "changed_edges_count": sum(1 for e in annotated_edges if e["change_status"] == "CHANGED"),
            "removed_edges_count": sum(1 for e in annotated_edges if e["change_status"] == "REMOVED"),
            "unchanged_edges_count": sum(1 for e in annotated_edges if e["change_status"] == "UNCHANGED")
        }
    }

@router.get("/paths")
def get_potential_attack_paths(
    current_user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    """
    Discovers potential attack paths for authenticated user's organization.
    """
    engine = GraphEngine(db, org_id)
    return engine.discover_potential_attack_paths()

@router.get("/blast-radius/{application_id}")
def get_application_blast_radius(
    application_id: str,
    current_user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    """
    Calculates application blast radius with BOLA tenant verification.
    """
    calculator = BlastRadiusCalculator(db, org_id)
    res = calculator.calculate_application_blast_radius(application_id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res

@router.get("/reachability/crown-jewels")
def get_crown_jewel_reachability(
    current_user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    """
    Queries crown jewel reachability for authenticated organization.
    """
    engine = GraphEngine(db, org_id)
    return engine.get_crown_jewel_reachability()


@router.get("/supply-chain")
def get_supply_chain_graph(
    current_user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    """
    Returns Multi-Tier Supply Chain Graph (Org -> Vendor -> Application -> DataAsset & Subprocessors).
    """
    from app.models import Vendor, Application, ApplicationInstance, DataAsset, AccessRelationship
    from app.models.vendor import SupplierProfile, SupplierSubprocessor

    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        return {"nodes": [], "edges": []}

    nodes = [{
        "id": f"org-{org.id}",
        "type": "organization",
        "data": {"label": org.name, "trust_boundary": "INTERNAL"},
        "position": {"x": 350, "y": 30}
    }]
    edges = []

    profiles = db.query(SupplierProfile).filter(SupplierProfile.organization_id == org_id).all()
    for idx, p in enumerate(profiles):
        v = p.vendor
        if not v:
            continue
        v_node_id = f"vendor-{v.id}"
        nodes.append({
            "id": v_node_id,
            "type": "vendor",
            "data": {
                "label": v.name,
                "tier": p.supply_chain_tier,
                "criticality": p.business_criticality,
                "supplier_risk": p.supplier_risk_score,
                "trust_boundary": "TIER_1_SUPPLIER"
            },
            "position": {"x": 80 + (idx * 200) % 800, "y": 180 + (idx // 4) * 150}
        })
        edges.append({
            "id": f"edge-org-{v.id}",
            "source": f"org-{org.id}",
            "target": v_node_id,
            "label": f"Tier {p.supply_chain_tier}",
            "style": {"stroke": "#64748b", "strokeWidth": 2}
        })

        # Subprocessors
        subs = db.query(SupplierSubprocessor).filter(SupplierSubprocessor.supplier_profile_id == p.id).all()
        for sub_idx, sub in enumerate(subs):
            sub_node_id = f"sub-{sub.id}"
            nodes.append({
                "id": sub_node_id,
                "type": "subprocessor",
                "data": {
                    "label": sub.subprocessor_name,
                    "service": sub.service_provided,
                    "tier": sub.tier,
                    "verification": sub.verification_status,
                    "trust_boundary": f"TIER_{sub.tier}_SUBPROCESSOR"
                },
                "position": {"x": 80 + (idx * 200) % 800 + (sub_idx * 60) - 30, "y": 380 + (idx // 4) * 150}
            })
            edges.append({
                "id": f"edge-v-{v.id}-sub-{sub.id}",
                "source": v_node_id,
                "target": sub_node_id,
                "label": sub.verification_status,
                "style": {"stroke": "#94a3b8", "strokeDasharray": "4 4"}
            })

    return {
        "organization": org.name,
        "nodes": nodes,
        "edges": edges
    }

