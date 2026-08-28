from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db, engine
from app.db.base_class import Base
from app.db.seed import seed_database
from app.models import Organization, ApplicationInstance, RiskFinding, DataAsset, SecuritySnapshot, User
from app.api.deps import get_current_user, get_current_org_id, require_role
from app.core.config import settings

router = APIRouter()

ADMIN_ROLES = ["SUPER_ADMIN", "SECURITY_ADMIN"]
REPORT_ROLES = ["SUPER_ADMIN", "SECURITY_ADMIN", "AUDITOR"]

@router.post("/reset")
def reset_demo_database(
    current_user: User = Depends(require_role(ADMIN_ROLES)),
    db: Session = Depends(get_db)
):
    """
    Resets the database tables and re-seeds the canonical Anurag Technologies
    demo dataset deterministically. Disabled in production mode (DEMO_MODE=False).
    """
    if not settings.DEMO_MODE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo database reset is disabled in production mode"
        )

    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        org = seed_database(db)
        return {
            "status": "SUCCESS",
            "message": "Demo database reset to canonical Anurag Technologies dataset.",
            "organization_name": org.name,
            "demo_mode": True,
            "security_posture_score": org.security_posture_score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset demo database: {str(e)}")

@router.get("/report")
def generate_executive_report(
    current_user: User = Depends(require_role(REPORT_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    """
    Generates a structured Executive Security Summary report payload for authenticated org.
    """
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    apps = db.query(ApplicationInstance).filter(ApplicationInstance.organization_id == org.id).all()
    findings = db.query(RiskFinding).filter(RiskFinding.organization_id == org.id).all()
    data_assets = db.query(DataAsset).filter(DataAsset.organization_id == org.id).all()
    snapshots = db.query(SecuritySnapshot).filter(SecuritySnapshot.organization_id == org.id).all()

    critical_apps = [a for a in apps if a.risk_severity == "Critical"]
    crown_jewels = [d for d in data_assets if d.is_crown_jewel]

    return {
        "report_type": "EXECUTIVE_SECURITY_SUMMARY",
        "organization_name": org.name,
        "domain": org.domain,
        "assessment_date": "2026-08-13",
        "security_posture_score": org.security_posture_score,
        "posture_severity": "High" if org.security_posture_score > 60 else "Medium",
        "total_monitored_applications": len(apps),
        "critical_risk_applications_count": len(critical_apps),
        "total_findings_count": len(findings),
        "critical_findings_count": sum(1 for f in findings if f.severity == "Critical"),
        "sensitive_data_assets_count": len(data_assets),
        "crown_jewel_assets_count": len(crown_jewels),
        "crown_jewels": [{"name": c.name, "system_of_record": c.system_of_record} for c in crown_jewels],
        "top_priorities": [
            {
                "priority": f"P{idx} - {f.severity.upper()}",
                "finding_title": f.title,
                "application": f.affected_application_name,
                "risk_contribution": f.risk_score_contribution,
                "recommended_action": f.remediations[0].title if f.remediations else f"Revoke excessive scopes on {f.affected_application_name}"
            }
            for idx, f in enumerate(findings) if f.severity in ("Critical", "High")
        ],
        "snapshots_recorded": len(snapshots),
        "disclaimer": "DEMO / SIMULATED ENVIRONMENT — All remediations are SIMULATION ONLY."
    }
