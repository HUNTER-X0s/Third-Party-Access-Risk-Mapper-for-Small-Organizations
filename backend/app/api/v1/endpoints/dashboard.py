from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Organization, ApplicationInstance, RiskFinding, PermissionGrant, DataAsset, User
from app.schemas.dashboard import DashboardSummaryOut
from app.schemas.finding import RiskFindingOut
from app.schemas.application import ApplicationInstanceOut
from app.api.deps import get_current_user, get_current_org_id

router = APIRouter()

@router.get("/dashboard", response_model=DashboardSummaryOut)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    """
    Returns SecOps Dashboard summary strictly scoped to the authenticated user's organization.
    """
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    apps = db.query(ApplicationInstance).filter(ApplicationInstance.organization_id == org.id).all()
    findings = db.query(RiskFinding).filter(RiskFinding.organization_id == org.id).all()
    excess_grants = db.query(PermissionGrant).join(ApplicationInstance).filter(
        ApplicationInstance.organization_id == org.id,
        PermissionGrant.is_excess == True
    ).all()
    data_assets = db.query(DataAsset).filter(DataAsset.organization_id == org.id).all()

    total_apps = len(apps)
    active_apps = sum(1 for a in apps if a.status == "active")
    shadow_apps = sum(1 for a in apps if a.is_shadow)
    dormant_apps = sum(1 for a in apps if a.status == "dormant")

    crit_count = sum(1 for f in findings if f.severity == "Critical")
    high_count = sum(1 for f in findings if f.severity == "High")

    dist = {
        "Critical": sum(1 for a in apps if a.risk_severity == "Critical"),
        "High": sum(1 for a in apps if a.risk_severity == "High"),
        "Medium": sum(1 for a in apps if a.risk_severity == "Medium"),
        "Low": sum(1 for a in apps if a.risk_severity == "Low"),
    }

    sorted_findings = sorted(findings, key=lambda f: 0 if f.severity == "Critical" else (1 if f.severity == "High" else 2))

    return DashboardSummaryOut(
        organization_name=org.name,
        security_posture_score=org.security_posture_score,
        total_applications=total_apps,
        active_applications=active_apps,
        shadow_applications=shadow_apps,
        dormant_applications=dormant_apps,
        critical_findings_count=crit_count,
        high_findings_count=high_count,
        total_excess_permissions=len(excess_grants),
        sensitive_data_assets_count=len(data_assets),
        data_freshness_status="CONFIRMED",
        risk_distribution=dist,
        top_findings=[RiskFindingOut.model_validate(f) for f in sorted_findings[:5]],
        applications=[ApplicationInstanceOut.model_validate(a) for a in apps]
    )

@router.get("/risk-summary")
def get_risk_summary(
    current_user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    apps = db.query(ApplicationInstance).filter(ApplicationInstance.organization_id == org.id).all()
    return {
        "organization_id": org.id,
        "security_posture_score": org.security_posture_score,
        "total_applications": len(apps),
        "risk_engine_version": "v1.5.0",
        "average_risk_score": round(sum(a.risk_score for a in apps) / len(apps), 1) if apps else 0.0
    }
