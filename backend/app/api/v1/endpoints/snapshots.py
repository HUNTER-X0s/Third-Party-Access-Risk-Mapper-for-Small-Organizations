from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import SecuritySnapshot, Organization, User
from app.schemas.snapshot import SecuritySnapshotOut, SecuritySnapshotCreate, SnapshotComparisonResponse
from app.services.snapshot_engine import SnapshotEngine
from app.api.deps import get_current_user, get_current_org_id, require_role

router = APIRouter()

ADMIN_ROLES = ["SUPER_ADMIN", "SECURITY_ADMIN"]

@router.get("", response_model=List[SecuritySnapshotOut])
def list_snapshots(
    current_user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    """
    Lists posture snapshots for authenticated organization.
    """
    snapshots = db.query(SecuritySnapshot).filter(
        SecuritySnapshot.organization_id == org_id
    ).order_by(SecuritySnapshot.created_at.desc()).all()
    return [SecuritySnapshotOut.model_validate(s) for s in snapshots]

@router.post("", response_model=SecuritySnapshotOut)
def create_snapshot(
    req: SecuritySnapshotCreate,
    current_user: User = Depends(require_role(ADMIN_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    """
    Creates a new security posture snapshot. Restricted to SUPER_ADMIN / SECURITY_ADMIN.
    """
    engine = SnapshotEngine(db, org_id)
    snapshot = engine.create_snapshot(req.snapshot_label, req.trigger_reason)
    return SecuritySnapshotOut.model_validate(snapshot)

@router.get("/{snapshot_id}/compare/{other_snapshot_id}", response_model=SnapshotComparisonResponse)
def compare_snapshots(
    snapshot_id: str,
    other_snapshot_id: str,
    current_user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    """
    Compares two posture snapshots with BOLA tenant verification.
    """
    engine = SnapshotEngine(db, org_id)
    try:
        res = engine.compare_snapshots(snapshot_id, other_snapshot_id)
        return SnapshotComparisonResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
