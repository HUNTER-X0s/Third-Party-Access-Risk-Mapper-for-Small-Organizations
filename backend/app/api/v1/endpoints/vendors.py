"""
api/v1/endpoints/vendors.py
Supplier / Vendor Risk Intelligence, C-SCRM Due Diligence & Supply Chain Governance Endpoints.
Aligned with NIST SP 1326 & NIST SP 800-161 Rev. 1.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models import (
    User, Vendor, Application, ApplicationInstance, DataAsset,
    AccessRelationship, AuditEvent
)
from app.models.vendor import (
    SupplierProfile, SupplierDueDiligence, SupplierSubprocessor, SupplierAssessmentHistory
)
from app.api.deps import get_current_user, get_current_org_id, require_role
from app.services.supplier_risk_engine import SupplierRiskEngine

router = APIRouter()

ALLOWED_ROLES = ["SUPER_ADMIN", "SECURITY_ADMIN", "IT_ADMIN", "AUDITOR", "APP_OWNER", "VIEWER"]
ASSESSMENT_WRITE_ROLES = ["SUPER_ADMIN", "SECURITY_ADMIN", "IT_ADMIN"]


class DueDiligenceUpdateRequest(BaseModel):
    foci_status: Optional[str] = "ASSESSED_NO_CONCERN"
    foci_details: Optional[str] = None
    provenance_status: Optional[str] = "ASSESSED"
    service_origin_country: Optional[str] = "United States"
    ownership_country: Optional[str] = "United States"
    hosting_provider: Optional[str] = "AWS / US-East"
    resilience_status: Optional[str] = "CURRENT"
    sla_availability_pct: Optional[float] = 99.9
    backup_recovery_tested: Optional[bool] = True
    bcp_dr_documented: Optional[bool] = True
    cyber_practices_status: Optional[str] = "STRONG"
    mfa_enforced: Optional[bool] = True
    vuln_mgmt_documented: Optional[bool] = True
    incident_response_tested: Optional[bool] = True
    encryption_in_transit_rest: Optional[bool] = True
    security_contact_email: Optional[str] = None
    notes: Optional[str] = None
    change_summary: Optional[str] = "Periodic due-diligence review"


class SupplierStatusUpdateRequest(BaseModel):
    status: str = "APPROVED"  # ACTIVE, UNDER_REVIEW, APPROVED, RESTRICTED, SUSPENDED, OFFBOARDED
    business_criticality: Optional[str] = "HIGH"  # LOW, MEDIUM, HIGH, CRITICAL


@router.get("")
def list_suppliers(
    status_filter: Optional[str] = Query(None, alias="status"),
    criticality: Optional[str] = None,
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """
    Lists all suppliers with aggregated access risk, supplier due diligence risk,
    business criticality, and assessment freshness.
    """
    vendors = db.query(Vendor).all()
    engine = SupplierRiskEngine(db, org_id)

    supplier_list = []
    for v in vendors:
        # Get or create org-scoped profile
        profile = db.query(SupplierProfile).filter(
            SupplierProfile.organization_id == org_id,
            SupplierProfile.vendor_id == v.id
        ).first()

        crit = profile.business_criticality if profile else engine.evaluate_supplier_criticality(v.id)
        stat = profile.status if profile else "ACTIVE"

        if status_filter and stat.upper() != status_filter.upper():
            continue
        if criticality and crit.upper() != criticality.upper():
            continue

        # Get connected application instances
        apps = db.query(ApplicationInstance).join(Application).filter(
            ApplicationInstance.organization_id == org_id,
            Application.vendor_id == v.id
        ).all()

        max_access_risk = max([a.risk_score for a in apps], default=0.0)
        app_names = [a.display_name for a in apps]

        # Check crown jewel access
        app_ids = [a.id for a in apps]
        has_crown_jewel = False
        if app_ids:
            has_crown_jewel = db.query(AccessRelationship).join(DataAsset).filter(
                AccessRelationship.organization_id == org_id,
                AccessRelationship.application_instance_id.in_(app_ids),
                DataAsset.is_crown_jewel == True
            ).count() > 0

        due_diligence = profile.due_diligence if profile else None
        supp_risk = profile.supplier_risk_score if profile else (100.0 - v.trust_score)

        supplier_list.append({
            "vendor_id": v.id,
            "profile_id": profile.id if profile else None,
            "name": v.name,
            "website": v.website,
            "status": stat,
            "business_criticality": crit,
            "supplier_risk_score": supp_risk,
            "access_risk_score": max_access_risk,
            "application_count": len(apps),
            "applications": app_names,
            "has_crown_jewel_access": has_crown_jewel,
            "assessment_status": profile.assessment_status if profile else "CURRENT",
            "last_reviewed_at": profile.last_reviewed_at.isoformat() if (profile and profile.last_reviewed_at) else None,
            "due_diligence_summary": {
                "foci": due_diligence.foci_status if due_diligence else "NOT_ASSESSED",
                "provenance": due_diligence.provenance_status if due_diligence else "UNKNOWN",
                "resilience": due_diligence.resilience_status if due_diligence else "UNKNOWN",
                "cyber_practices": due_diligence.cyber_practices_status if due_diligence else "UNKNOWN"
            } if due_diligence else None,
            "is_synthetic_demo": True
        })

    return {
        "organization_id": org_id,
        "total_suppliers": len(supplier_list),
        "suppliers": sorted(supplier_list, key=lambda x: x["access_risk_score"], reverse=True)
    }


@router.get("/priority-queue")
def get_supplier_priority_queue(
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """
    Returns deterministic Supplier Review Priority Queue (P0 / P1 / P2).
    """
    engine = SupplierRiskEngine(db, org_id)
    queue = engine.get_supplier_priority_queue()
    return {
        "organization_id": org_id,
        "total_queued": len(queue),
        "queue": queue
    }


@router.get("/concentration")
def get_supplier_concentration_risks(
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """
    Evaluates dependency concentration across suppliers, critical data assets, and processes.
    """
    engine = SupplierRiskEngine(db, org_id)
    risks = engine.calculate_concentration_risk()
    return {
        "organization_id": org_id,
        "concentration_analysis": risks
    }


@router.get("/{vendor_id}")
def get_supplier_details(
    vendor_id: str,
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """
    Returns comprehensive supplier investigation profile including NIST SP 1326 due diligence,
    downstream subprocessors, accessible assets, and assessment version history.
    """
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found.")

    profile = db.query(SupplierProfile).filter(
        SupplierProfile.organization_id == org_id,
        SupplierProfile.vendor_id == vendor.id
    ).first()

    # Get apps
    apps = db.query(ApplicationInstance).join(Application).filter(
        ApplicationInstance.organization_id == org_id,
        Application.vendor_id == vendor.id
    ).all()

    app_ids = [a.id for a in apps]

    # Reachable data assets
    relationships = db.query(AccessRelationship).filter(
        AccessRelationship.organization_id == org_id,
        AccessRelationship.application_instance_id.in_(app_ids)
    ).all() if app_ids else []

    asset_ids = list(set(r.data_asset_id for r in relationships))
    assets = db.query(DataAsset).filter(DataAsset.id.in_(asset_ids)).all() if asset_ids else []

    # Subprocessors
    subprocessors = []
    if profile:
        subs = db.query(SupplierSubprocessor).filter(
            SupplierSubprocessor.supplier_profile_id == profile.id
        ).all()
        subprocessors = [
            {
                "id": s.id,
                "name": s.subprocessor_name,
                "service": s.service_provided,
                "data_shared": s.data_shared_categories or [],
                "hosting_region": s.hosting_region,
                "verification_status": s.verification_status,
                "tier": s.tier,
                "evidence_refs": s.evidence_refs or []
            }
            for s in subs
        ]

    # Assessment history
    history = []
    if profile:
        hist_records = db.query(SupplierAssessmentHistory).filter(
            SupplierAssessmentHistory.supplier_profile_id == profile.id
        ).order_by(SupplierAssessmentHistory.version.desc()).all()
        history = [
            {
                "id": h.id,
                "version": h.version,
                "change_summary": h.change_summary,
                "reviewed_by": h.reviewed_by,
                "created_at": h.created_at.isoformat() if h.created_at else None
            }
            for h in hist_records
        ]

    dd = profile.due_diligence if profile else None

    return {
        "vendor": {
            "id": vendor.id,
            "name": vendor.name,
            "website": vendor.website,
            "trust_score": vendor.trust_score,
            "soc2_status": vendor.soc2_status,
            "iso27001_certified": vendor.iso27001_certified
        },
        "profile": {
            "id": profile.id if profile else None,
            "status": profile.status if profile else "ACTIVE",
            "business_criticality": profile.business_criticality if profile else "MEDIUM",
            "supplier_risk_score": profile.supplier_risk_score if profile else 50.0,
            "supplier_risk_severity": profile.supplier_risk_severity if profile else "Medium",
            "primary_business_owner": profile.primary_business_owner if profile else None,
            "security_owner": profile.security_owner if profile else None,
            "assessment_status": profile.assessment_status if profile else "CURRENT",
            "last_reviewed_at": profile.last_reviewed_at.isoformat() if (profile and profile.last_reviewed_at) else None,
            "next_review_due": profile.next_review_due.isoformat() if (profile and profile.next_review_due) else None
        },
        "due_diligence": {
            "foci": {
                "status": dd.foci_status if dd else "NOT_ASSESSED",
                "details": dd.foci_details if dd else None,
                "source": dd.foci_source if dd else "MANUAL_ASSESSMENT",
                "confidence": dd.foci_confidence if dd else "MEDIUM"
            },
            "provenance": {
                "status": dd.provenance_status if dd else "UNKNOWN",
                "service_origin_country": dd.service_origin_country if dd else "United States",
                "ownership_country": dd.ownership_country if dd else "United States",
                "hosting_provider": dd.hosting_provider if dd else "AWS / US-East",
                "notes": dd.provenance_notes if dd else None
            },
            "resilience": {
                "status": dd.resilience_status if dd else "UNKNOWN",
                "sla_availability_pct": dd.sla_availability_pct if dd else 99.9,
                "backup_recovery_tested": dd.backup_recovery_tested if dd else False,
                "bcp_dr_documented": dd.bcp_dr_documented if dd else False,
                "notes": dd.resilience_notes if dd else None
            },
            "cyber_practices": {
                "status": dd.cyber_practices_status if dd else "UNKNOWN",
                "mfa_enforced": dd.mfa_enforced if dd else False,
                "vuln_mgmt_documented": dd.vuln_mgmt_documented if dd else False,
                "incident_response_tested": dd.incident_response_tested if dd else False,
                "encryption_in_transit_rest": dd.encryption_in_transit_rest if dd else True,
                "security_contact_email": dd.security_contact_email if dd else None,
                "notes": dd.cyber_practices_notes if dd else None
            },
            "version": dd.version if dd else 1,
            "evidence_refs": dd.evidence_refs if dd else ["EV-101", "EV-217"],
            "last_verified_at": dd.last_verified_at.isoformat() if (dd and dd.last_verified_at) else None,
            "reviewed_by": dd.reviewed_by if dd else "Security Analyst"
        } if dd else None,
        "applications": [
            {
                "id": a.id,
                "display_name": a.display_name,
                "risk_score": a.risk_score,
                "risk_severity": a.risk_severity,
                "status": a.status
            }
            for a in apps
        ],
        "accessible_data_assets": [
            {
                "id": d.id,
                "name": d.name,
                "system": d.system_of_record,
                "is_crown_jewel": d.is_crown_jewel,
                "sensitivity": d.classification.sensitivity_level if d.classification else 3
            }
            for d in assets
        ],
        "subprocessors": subprocessors,
        "assessment_history": history,
        "is_synthetic_demo": True
    }


@router.post("/{vendor_id}/assess")
def update_supplier_due_diligence(
    vendor_id: str,
    body: DueDiligenceUpdateRequest,
    current_user: User = Depends(require_role(ASSESSMENT_WRITE_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """
    Updates NIST SP 1326 due diligence assessment for a supplier.
    Enforces server-side RBAC, records immutable assessment version history, and logs AuditEvent.
    """
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found.")

    profile = db.query(SupplierProfile).filter(
        SupplierProfile.organization_id == org_id,
        SupplierProfile.vendor_id == vendor.id
    ).first()

    if not profile:
        profile = SupplierProfile(
            organization_id=org_id,
            vendor_id=vendor.id,
            status="ACTIVE",
            business_criticality="HIGH"
        )
        db.add(profile)
        db.flush()

    dd = db.query(SupplierDueDiligence).filter(
        SupplierDueDiligence.supplier_profile_id == profile.id
    ).first()

    if not dd:
        dd = SupplierDueDiligence(
            supplier_profile_id=profile.id,
            version=1
        )
        db.add(dd)

    # Update DD fields
    dd.foci_status = body.foci_status or dd.foci_status
    dd.foci_details = body.foci_details or dd.foci_details
    dd.provenance_status = body.provenance_status or dd.provenance_status
    dd.service_origin_country = body.service_origin_country or dd.service_origin_country
    dd.ownership_country = body.ownership_country or dd.ownership_country
    dd.hosting_provider = body.hosting_provider or dd.hosting_provider
    dd.resilience_status = body.resilience_status or dd.resilience_status
    dd.sla_availability_pct = body.sla_availability_pct if body.sla_availability_pct is not None else dd.sla_availability_pct
    dd.backup_recovery_tested = body.backup_recovery_tested if body.backup_recovery_tested is not None else dd.backup_recovery_tested
    dd.bcp_dr_documented = body.bcp_dr_documented if body.bcp_dr_documented is not None else dd.bcp_dr_documented
    dd.cyber_practices_status = body.cyber_practices_status or dd.cyber_practices_status
    dd.mfa_enforced = body.mfa_enforced if body.mfa_enforced is not None else dd.mfa_enforced
    dd.vuln_mgmt_documented = body.vuln_mgmt_documented if body.vuln_mgmt_documented is not None else dd.vuln_mgmt_documented
    dd.incident_response_tested = body.incident_response_tested if body.incident_response_tested is not None else dd.incident_response_tested
    dd.encryption_in_transit_rest = body.encryption_in_transit_rest if body.encryption_in_transit_rest is not None else dd.encryption_in_transit_rest
    dd.security_contact_email = body.security_contact_email or dd.security_contact_email
    dd.notes = body.notes or dd.notes
    dd.version += 1
    dd.reviewed_by = current_user.email
    dd.last_verified_at = datetime.now(timezone.utc)

    # Re-calculate supplier due diligence score
    engine = SupplierRiskEngine(db, org_id)
    score_res = engine.calculate_due_diligence_score(dd)
    profile.supplier_risk_score = score_res["supplier_risk_score"]
    profile.supplier_risk_severity = score_res["supplier_risk_severity"]
    profile.last_reviewed_at = datetime.now(timezone.utc)
    profile.assessment_status = "CURRENT"

    # Record versioned history snapshot
    history_record = SupplierAssessmentHistory(
        supplier_profile_id=profile.id,
        version=dd.version,
        assessment_snapshot_json={
            "foci_status": dd.foci_status,
            "provenance_status": dd.provenance_status,
            "resilience_status": dd.resilience_status,
            "cyber_practices_status": dd.cyber_practices_status,
            "supplier_risk_score": profile.supplier_risk_score
        },
        change_summary=body.change_summary or "Manual due-diligence review",
        reviewed_by=current_user.email
    )
    db.add(history_record)

    # Audit Trail
    audit = AuditEvent(
        organization_id=org_id,
        actor_email=current_user.email,
        action="SUPPLIER_ASSESSMENT_UPDATED",
        target_type="SupplierProfile",
        target_id=profile.id,
        outcome="SUCCESS",
        event_metadata={
            "vendor_name": vendor.name,
            "version": dd.version,
            "new_supplier_risk_score": profile.supplier_risk_score
        }
    )
    db.add(audit)
    db.commit()

    return {
        "message": "Supplier due diligence assessment updated successfully",
        "vendor_id": vendor.id,
        "version": dd.version,
        "supplier_risk_score": profile.supplier_risk_score,
        "supplier_risk_severity": profile.supplier_risk_severity
    }


@router.get("/{vendor_id}/impact-analysis")
def simulate_supplier_failure_impact(
    vendor_id: str,
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """
    Simulates deterministic business impact if the supplier becomes unavailable.
    """
    engine = SupplierRiskEngine(db, org_id)
    res = engine.simulate_single_supplier_failure(vendor_id)
    if "error" in res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=res["error"])
    return res


@router.get("/{vendor_id}/explain")
def explain_supplier_risk(
    vendor_id: str,
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """
    Returns deterministic factor breakdown explaining the supplier risk score.
    """
    engine = SupplierRiskEngine(db, org_id)
    res = engine.explain_supplier_risk(vendor_id)
    if "error" in res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=res["error"])
    return res

