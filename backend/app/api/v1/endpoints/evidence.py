from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import RawEvidence, User
from app.schemas.evidence import RawEvidenceOut
from app.services.evidence_engine import verify_payload_hash
from app.api.deps import get_current_user, get_current_org_id, require_role

router = APIRouter()

EVIDENCE_ROLES = ["SUPER_ADMIN", "SECURITY_ADMIN", "AUDITOR"]

@router.get("/{evidence_id}", response_model=RawEvidenceOut)
def get_evidence(
    evidence_id: str,
    current_user: User = Depends(require_role(EVIDENCE_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    """
    Retrieves raw evidence with role restriction and server-side BOLA check.
    """
    ev = db.query(RawEvidence).filter(
        RawEvidence.id == evidence_id,
        RawEvidence.organization_id == org_id
    ).first()

    if not ev:
        raise HTTPException(status_code=404, detail="Raw evidence not found")

    return RawEvidenceOut.model_validate(ev)

@router.get("/{evidence_id}/verify")
def verify_evidence_integrity(
    evidence_id: str,
    current_user: User = Depends(require_role(EVIDENCE_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db)
):
    """
    Verifies payload hash SHA-256 integrity status for raw evidence.
    """
    ev = db.query(RawEvidence).filter(
        RawEvidence.id == evidence_id,
        RawEvidence.organization_id == org_id
    ).first()

    if not ev:
        raise HTTPException(status_code=404, detail="Raw evidence not found")

    res = verify_payload_hash(ev.raw_payload_json, ev.payload_hash_sha256)
    return {
        "evidence_id": ev.id,
        "organization_id": ev.organization_id,
        "collected_at": ev.collected_at,
        "verification_result": res
    }
