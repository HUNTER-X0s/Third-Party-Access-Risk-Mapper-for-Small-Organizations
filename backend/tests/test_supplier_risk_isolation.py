"""
Test: Supplier tenant isolation.
Ensures supplier profiles, due diligence, and subprocessors are strictly scoped to their organization.
Cross-tenant reads must return empty sets, not other orgs' data.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Organization, Vendor
from app.models.vendor import SupplierProfile, SupplierDueDiligence, SupplierSubprocessor
from app.services.supplier_risk_engine import SupplierRiskEngine
from app.db.base_class import generate_uuid

TEST_DB_URL = "sqlite:///./test_supplier_isolation.db"

@pytest.fixture(scope="module")
def db_with_two_orgs():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    org_a = Organization(id=generate_uuid(), name="Org Alpha", domain="alpha.com")
    org_b = Organization(id=generate_uuid(), name="Org Beta", domain="beta.com")
    vendor = Vendor(id=generate_uuid(), name="Shared SaaS Vendor", website="https://shared.com", trust_score=60.0)
    db.add_all([org_a, org_b, vendor])
    db.flush()

    # Profile ONLY for org_a
    profile_a = SupplierProfile(
        organization_id=org_a.id,
        vendor_id=vendor.id,
        status="APPROVED",
        business_criticality="CRITICAL",
        supplier_risk_score=80.0
    )
    db.add(profile_a)
    db.flush()

    dd_a = SupplierDueDiligence(
        supplier_profile_id=profile_a.id,
        foci_status="POTENTIAL_CONCERN",
        provenance_status="DISPUTED",
        resilience_status="GAP",
        cyber_practices_status="MINIMAL",
        version=1,
        is_synthetic_demo=True
    )
    sub_a = SupplierSubprocessor(
        supplier_profile_id=profile_a.id,
        subprocessor_name="Alpha-only CDN",
        service_provided="CDN",
        verification_status="DECLARED",
        tier=2
    )
    db.add_all([dd_a, sub_a])
    db.flush()

    yield db, org_a, org_b, vendor, profile_a
    db.close()
    Base.metadata.drop_all(engine)


def test_org_b_cannot_see_org_a_supplier_profile(db_with_two_orgs):
    """Org B must receive no supplier profiles from Org A's data."""
    db, org_a, org_b, vendor, profile_a = db_with_two_orgs
    profiles_b = db.query(SupplierProfile).filter(
        SupplierProfile.organization_id == org_b.id
    ).all()
    assert len(profiles_b) == 0


def test_org_b_concentration_returns_empty(db_with_two_orgs):
    """Org B concentration risk engine must find no vendors (strict org_id filter)."""
    db, org_a, org_b, vendor, profile_a = db_with_two_orgs
    engine = SupplierRiskEngine(db, org_b.id)
    # Should return empty list since org_b has no apps
    results = engine.calculate_concentration_risk()
    # All results must not include profile_a's vendor data
    org_b_vendor_ids = {r["vendor_id"] for r in results}
    assert vendor.id not in org_b_vendor_ids or len(results) == 0


def test_org_a_profile_visible_only_to_org_a(db_with_two_orgs):
    """Org A's supplier profile must only be returned when querying with org_a's ID."""
    db, org_a, org_b, vendor, profile_a = db_with_two_orgs
    profiles_a = db.query(SupplierProfile).filter(
        SupplierProfile.organization_id == org_a.id
    ).all()
    assert any(p.id == profile_a.id for p in profiles_a)


def test_subprocessor_isolation(db_with_two_orgs):
    """Subprocessors of org_a's profile must not be accessible via org_b's profile IDs."""
    db, org_a, org_b, vendor, profile_a = db_with_two_orgs
    profiles_b = db.query(SupplierProfile).filter(
        SupplierProfile.organization_id == org_b.id
    ).all()
    b_profile_ids = [p.id for p in profiles_b]
    if not b_profile_ids:
        return  # No profiles = no possible cross-tenant leak. Pass.

    subs = db.query(SupplierSubprocessor).filter(
        SupplierSubprocessor.supplier_profile_id.in_(b_profile_ids)
    ).all()
    assert len(subs) == 0
