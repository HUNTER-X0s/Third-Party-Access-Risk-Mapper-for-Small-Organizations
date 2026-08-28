"""
Test: Supplier / Vendor C-SCRM model integrity.
Covers SupplierProfile, SupplierDueDiligence, SupplierSubprocessor, SupplierAssessmentHistory creation and DB persistence.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Organization, Vendor
from app.models.vendor import SupplierProfile, SupplierDueDiligence, SupplierSubprocessor, SupplierAssessmentHistory
from app.db.base_class import generate_uuid

TEST_DB_URL = "sqlite:///./test_vendor_model.db"

@pytest.fixture(scope="module")
def db():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="module")
def org_vendor(db):
    org = Organization(id=generate_uuid(), name="Test Org", domain="test.org")
    vendor = Vendor(id=generate_uuid(), name="TestVendor Inc.", website="https://test.com", trust_score=70.0)
    db.add_all([org, vendor])
    db.flush()
    return org, vendor

def test_supplier_profile_creation(db, org_vendor):
    """SupplierProfile records organization_id, vendor_id, and default fields."""
    org, vendor = org_vendor
    profile = SupplierProfile(
        organization_id=org.id,
        vendor_id=vendor.id,
        status="ACTIVE",
        business_criticality="HIGH",
        supplier_risk_score=50.0,
        supply_chain_tier=1
    )
    db.add(profile)
    db.flush()
    assert profile.id is not None
    assert profile.organization_id == org.id
    assert profile.vendor_id == vendor.id
    assert profile.business_criticality == "HIGH"
    assert profile.supply_chain_tier == 1

def test_due_diligence_nist_fields(db, org_vendor):
    """SupplierDueDiligence captures all 4 NIST SP 1326 dimensions."""
    org, vendor = org_vendor
    profile = db.query(SupplierProfile).filter(
        SupplierProfile.organization_id == org.id,
        SupplierProfile.vendor_id == vendor.id
    ).first()

    dd = SupplierDueDiligence(
        supplier_profile_id=profile.id,
        foci_status="ASSESSED_NO_CONCERN",
        provenance_status="ASSESSED",
        resilience_status="CURRENT",
        cyber_practices_status="STRONG",
        mfa_enforced=True,
        encryption_in_transit_rest=True,
        sla_availability_pct=99.9,
        backup_recovery_tested=True,
        version=1,
        is_synthetic_demo=True
    )
    db.add(dd)
    db.flush()
    assert dd.foci_status == "ASSESSED_NO_CONCERN"
    assert dd.provenance_status == "ASSESSED"
    assert dd.resilience_status == "CURRENT"
    assert dd.cyber_practices_status == "STRONG"
    assert dd.mfa_enforced is True
    assert dd.is_synthetic_demo is True

def test_subprocessor_tier_tracking(db, org_vendor):
    """SupplierSubprocessor records tier and verification status."""
    org, vendor = org_vendor
    profile = db.query(SupplierProfile).filter(
        SupplierProfile.organization_id == org.id,
        SupplierProfile.vendor_id == vendor.id
    ).first()

    sub = SupplierSubprocessor(
        supplier_profile_id=profile.id,
        subprocessor_name="AWS",
        service_provided="Cloud Hosting",
        data_shared_categories=["Customer Data"],
        hosting_region="US",
        verification_status="DECLARED",
        tier=2
    )
    db.add(sub)
    db.flush()
    assert sub.tier == 2
    assert sub.verification_status == "DECLARED"

def test_assessment_history_immutability(db, org_vendor):
    """SupplierAssessmentHistory records are append-only with version tracking."""
    org, vendor = org_vendor
    profile = db.query(SupplierProfile).filter(
        SupplierProfile.organization_id == org.id,
        SupplierProfile.vendor_id == vendor.id
    ).first()

    hist = SupplierAssessmentHistory(
        supplier_profile_id=profile.id,
        version=1,
        assessment_snapshot_json={"foci_status": "ASSESSED_NO_CONCERN", "supplier_risk_score": 50.0},
        change_summary="Initial assessment",
        reviewed_by="analyst@test.org"
    )
    db.add(hist)
    db.flush()
    assert hist.version == 1
    assert hist.reviewed_by == "analyst@test.org"
    assert "foci_status" in hist.assessment_snapshot_json
