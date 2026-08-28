from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import ApplicationInstance, PermissionGrant, AccessRelationship, RiskFinding, User
from app.schemas.application import ApplicationInstanceOut
from app.schemas.permission import PermissionGrantOut
from app.schemas.data_asset import AccessRelationshipOut
from app.schemas.finding import RiskFindingOut
from app.api.deps import get_current_user, get_current_org_id

router = APIRouter()

@router.get("", response_model=List[ApplicationInstanceOut])
def list_applications(
    current_user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    """
    Lists monitored application instances strictly scoped to the authenticated user's organization.
    """
    query = db.query(ApplicationInstance).filter(ApplicationInstance.organization_id == org_id)

    # Object-level authorization for APP_OWNER: show assigned apps only
    if current_user.role == "APP_OWNER":
        query = query.filter(ApplicationInstance.authorized_by_email == current_user.email)

    apps = query.all()
    return [ApplicationInstanceOut.model_validate(a) for a in apps]

@router.get("/{app_id}", response_model=ApplicationInstanceOut)
def get_application(
    app_id: str,
    current_user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    """
    Retrieves application details with server-enforced tenant and BOLA check.
    """
    app_inst = db.query(ApplicationInstance).filter(
        ApplicationInstance.id == app_id,
        ApplicationInstance.organization_id == org_id
    ).first()

    if not app_inst:
        raise HTTPException(status_code=404, detail="Application instance not found")

    if current_user.role == "APP_OWNER" and app_inst.authorized_by_email != current_user.email:
        raise HTTPException(status_code=404, detail="Application instance not found")

    return ApplicationInstanceOut.model_validate(app_inst)

@router.get("/{app_id}/permissions", response_model=List[PermissionGrantOut])
def get_application_permissions(
    app_id: str,
    current_user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    app_inst = db.query(ApplicationInstance).filter(
        ApplicationInstance.id == app_id,
        ApplicationInstance.organization_id == org_id
    ).first()

    if not app_inst:
        raise HTTPException(status_code=404, detail="Application instance not found")

    grants = db.query(PermissionGrant).filter(PermissionGrant.application_instance_id == app_id).all()
    return [PermissionGrantOut.model_validate(g) for g in grants]

@router.get("/{app_id}/data", response_model=List[AccessRelationshipOut])
def get_application_data_access(
    app_id: str,
    current_user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    app_inst = db.query(ApplicationInstance).filter(
        ApplicationInstance.id == app_id,
        ApplicationInstance.organization_id == org_id
    ).first()

    if not app_inst:
        raise HTTPException(status_code=404, detail="Application instance not found")

    relationships = db.query(AccessRelationship).filter(AccessRelationship.application_instance_id == app_id).all()
    return [AccessRelationshipOut.model_validate(r) for r in relationships]

@router.get("/{app_id}/findings", response_model=List[RiskFindingOut])
def get_application_findings(
    app_id: str,
    current_user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    app_inst = db.query(ApplicationInstance).filter(
        ApplicationInstance.id == app_id,
        ApplicationInstance.organization_id == org_id
    ).first()

    if not app_inst:
        raise HTTPException(status_code=404, detail="Application instance not found")

    findings = db.query(RiskFinding).filter(RiskFinding.application_instance_id == app_id).all()
    return [RiskFindingOut.model_validate(f) for f in findings]
