"""
Test: NIST SP 1326 Due Diligence Score Engine.
Validates deterministic scoring for FOCI, Provenance, Resilience, and Foundational Cyber Practices.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Organization, Vendor
from app.models.vendor import SupplierProfile, SupplierDueDiligence
from app.services.supplier_risk_engine import SupplierRiskEngine
from app.db.base_class import generate_uuid

TEST_DB_URL = "sqlite:///./test_nist_dd.db"

@pytest.fixture(scope="module")
def setup():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    org = Organization(id=generate_uuid(), name="NIST Test Org", domain="nist-test.org")
    vendor = Vendor(id=generate_uuid(), name="NIST Test Vendor", website="https://nist-test.com", trust_score=60.0)
    db.add_all([org, vendor])
    db.flush()

    profile = SupplierProfile(
        organization_id=org.id,
        vendor_id=vendor.id,
        status="ACTIVE",
        business_criticality="HIGH"
    )
    db.add(profile)
    db.flush()

    yield db, org, vendor, profile
    db.close()
    Base.metadata.drop_all(engine)

def make_dd(profile_id, foci, prov, res, cyber, mfa=True, backup=True):
    return SupplierDueDiligence(
        supplier_profile_id=profile_id,
        foci_status=foci,
        provenance_status=prov,
        resilience_status=res,
        cyber_practices_status=cyber,
        mfa_enforced=mfa,
        backup_recovery_tested=backup,
        version=1,
        is_synthetic_demo=True
    )

def test_perfect_due_diligence_low_risk(setup):
    """Supplier with all green NIST dimensions should score low (Low severity)."""
    db, org, vendor, profile = setup
    dd = make_dd(profile.id, "ASSESSED_NO_CONCERN", "ASSESSED", "CURRENT", "STRONG")
    engine = SupplierRiskEngine(db, org.id)
    result = engine.calculate_due_diligence_score(dd)
    assert result["supplier_risk_score"] <= 30.0
    assert result["supplier_risk_severity"] == "Low"

def test_critical_foci_concern_elevates_score(setup):
    """POTENTIAL_CONCERN FOCI with MINIMAL cyber practices should yield Critical or High."""
    db, org, vendor, profile = setup
    dd = make_dd(profile.id, "POTENTIAL_CONCERN", "DISPUTED", "GAP", "MINIMAL", mfa=False, backup=False)
    engine = SupplierRiskEngine(db, org.id)
    result = engine.calculate_due_diligence_score(dd)
    assert result["supplier_risk_score"] >= 60.0
    assert result["supplier_risk_severity"] in ("Critical", "High")

def test_unknown_dimensions_medium_risk(setup):
    """All UNKNOWN dimensions should produce a medium-to-high risk score."""
    db, org, vendor, profile = setup
    dd = make_dd(profile.id, "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN", mfa=False, backup=False)
    engine = SupplierRiskEngine(db, org.id)
    result = engine.calculate_due_diligence_score(dd)
    assert result["supplier_risk_score"] >= 30.0
    assert result["supplier_risk_severity"] in ("Medium", "High", "Critical")

def test_score_clamp_bounds(setup):
    """Score is always clamped between 5.0 and 95.0."""
    db, org, vendor, profile = setup
    for foci in ["ASSESSED_NO_CONCERN", "POTENTIAL_CONCERN", "UNKNOWN", "NOT_ASSESSED"]:
        dd = make_dd(profile.id, foci, "UNKNOWN", "UNKNOWN", "UNKNOWN")
        engine = SupplierRiskEngine(db, org.id)
        result = engine.calculate_due_diligence_score(dd)
        assert 5.0 <= result["supplier_risk_score"] <= 95.0

def test_dimension_breakdown_present(setup):
    """Score result must include all 4 NIST dimension sub-scores."""
    db, org, vendor, profile = setup
    dd = make_dd(profile.id, "ASSESSED_NO_CONCERN", "ASSESSED", "CURRENT", "STRONG")
    engine = SupplierRiskEngine(db, org.id)
    result = engine.calculate_due_diligence_score(dd)
    dims = result["dimensions"]
    assert "foci_risk" in dims
    assert "provenance_risk" in dims
    assert "resilience_risk" in dims
    assert "foundational_cyber_risk" in dims
