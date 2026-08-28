from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import RiskFinding, ApplicationInstance, PermissionGrant, DataAsset, AccessRelationship, AuditEvent, Organization, User
from app.schemas.finding import RiskFindingOut, SimulationRequest, SimulationResponse
from app.services.remediation_simulator import simulate_remediation
from app.services.remediation_optimizer import RemediationOptimizer
from app.api.deps import get_current_user, get_current_org_id, require_role

SIMULATION_ROLES = ["SUPER_ADMIN", "SECURITY_ADMIN", "APP_OWNER"]
READ_ROLES = ["SUPER_ADMIN", "SECURITY_ADMIN", "AUDITOR", "APP_OWNER", "VIEWER"]

router = APIRouter()

@router.get("", response_model=List[RiskFindingOut])
def list_findings(
    current_user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    """
    Lists risk findings strictly scoped to the authenticated user's organization.
    """
    query = db.query(RiskFinding).filter(RiskFinding.organization_id == org_id)

    # APP_OWNER restriction
    if current_user.role == "APP_OWNER":
        query = query.join(ApplicationInstance).filter(ApplicationInstance.authorized_by_email == current_user.email)

    findings = query.all()
    return [RiskFindingOut.model_validate(f) for f in findings]

@router.get("/{finding_id}", response_model=RiskFindingOut)
def get_finding(
    finding_id: str,
    current_user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    """
    Retrieves finding details with BOLA tenant ownership check.
    """
    finding = db.query(RiskFinding).filter(
        RiskFinding.id == finding_id,
        RiskFinding.organization_id == org_id
    ).first()

    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    return RiskFindingOut.model_validate(finding)

@router.post("/{finding_id}/simulate-remediation", response_model=SimulationResponse)
def simulate_finding_remediation(
    finding_id: str,
    req: SimulationRequest,
    current_user: User = Depends(require_role(SIMULATION_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    """
    Simulates remediation for finding with BOLA tenant check and actor audit logging.
    """
    finding = db.query(RiskFinding).filter(
        RiskFinding.id == finding_id,
        RiskFinding.organization_id == org_id
    ).first()

    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    app_inst = db.query(ApplicationInstance).filter(
        ApplicationInstance.id == finding.application_instance_id,
        ApplicationInstance.organization_id == org_id
    ).first()

    if not app_inst:
        raise HTTPException(status_code=404, detail="Application instance not found")

    grants = db.query(PermissionGrant).filter(PermissionGrant.application_instance_id == app_inst.id).all()
    all_scopes = [g.raw_scope for g in grants]

    revoked_scopes = req.revoked_scopes
    remaining_scopes = [s for s in all_scopes if s not in revoked_scopes]

    excess_count = sum(1 for g in grants if g.is_excess)
    excess_ratio = (excess_count / len(grants)) if grants else 0.0

    rel = db.query(AccessRelationship).filter(AccessRelationship.application_instance_id == app_inst.id).first()
    data_sens = 3
    is_crown = False
    if rel:
        da = db.query(DataAsset).filter(DataAsset.id == rel.data_asset_id).first()
        if da:
            data_sens = da.classification.sensitivity_level
            is_crown = da.is_crown_jewel

    current_risk_input = {
        "max_scope_severity": "Critical" if any(g.permission.severity_level == "Critical" for g in grants) else "High",
        "excess_ratio": excess_ratio,
        "max_data_sensitivity": data_sens,
        "system_criticality": 4,
        "vendor_trust_score": app_inst.application.vendor.trust_score if app_inst.application and app_inst.application.vendor else 70.0,
        "is_shadow": app_inst.is_shadow,
        "in_attack_path": True,
        "is_crown_jewel_exposed": is_crown
    }

    res = simulate_remediation(current_risk_input, revoked_scopes, remaining_scopes)

    audit = AuditEvent(
        organization_id=org_id,
        actor_email=current_user.email,
        action="SIMULATION_EXECUTED",
        target_type="RiskFinding",
        target_id=finding.id,
        outcome="SUCCESS",
        event_metadata={"revoked_scopes": revoked_scopes, "simulated_score": res["simulated_score"]}
    )
    db.add(audit)
    db.commit()

    return SimulationResponse(**res)

@router.get("/{finding_id}/remediation-analysis")
def get_remediation_analysis(
    finding_id: str,
    current_user: User = Depends(require_role(SIMULATION_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    """
    Calculates minimum effective remediation analysis for finding.
    """
    finding = db.query(RiskFinding).filter(
        RiskFinding.id == finding_id,
        RiskFinding.organization_id == org_id
    ).first()

    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    optimizer = RemediationOptimizer(db, org_id)
    res = optimizer.calculate_minimum_effective_remediation(finding_id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res
