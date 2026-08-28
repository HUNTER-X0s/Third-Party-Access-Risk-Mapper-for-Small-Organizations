"""
Test: Supplier concentration and failure impact simulation.
Ensures concentration scores are deterministic and impact simulation stays within bounds.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Organization, Vendor, Application, ApplicationInstance, DataAsset, DataClassification, AccessRelationship
from app.services.supplier_risk_engine import SupplierRiskEngine
from app.db.base_class import generate_uuid

TEST_DB_URL = "sqlite:///./test_supplier_conc.db"

@pytest.fixture(scope="module")
def db_setup():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    org = Organization(id=generate_uuid(), name="Conc Test Org", domain="conc-test.org")
    vendor = Vendor(id=generate_uuid(), name="MassiveCloud Inc.", website="https://massivecloud.com", trust_score=70.0)
    db.add_all([org, vendor])
    db.flush()

    dc = DataClassification(
        id=generate_uuid(), name="Secret", display_name="Secret Data",
        sensitivity_level=5
    )
    db.add(dc)
    db.flush()

    app1 = Application(id=generate_uuid(), vendor_id=vendor.id, canonical_name="CloudApp1", category="SaaS")
    app2 = Application(id=generate_uuid(), vendor_id=vendor.id, canonical_name="CloudApp2", category="SaaS")
    db.add_all([app1, app2])
    db.flush()

    ai1 = ApplicationInstance(
        id=generate_uuid(), organization_id=org.id, application_id=app1.id,
        display_name="CloudApp1 Prod", status="active", authorized_by_email="admin@conc-test.org",
        risk_score=75.0, risk_severity="High"
    )
    ai2 = ApplicationInstance(
        id=generate_uuid(), organization_id=org.id, application_id=app2.id,
        display_name="CloudApp2 Prod", status="active", authorized_by_email="admin@conc-test.org",
        risk_score=60.0, risk_severity="High"
    )
    db.add_all([ai1, ai2])
    db.flush()

    asset1 = DataAsset(
        id=generate_uuid(), organization_id=org.id, classification_id=dc.id, name="Crown Asset",
        system_of_record="InternalDB", is_crown_jewel=True
    )
    db.add(asset1)
    db.flush()

    rel1 = AccessRelationship(
        id=generate_uuid(), organization_id=org.id,
        application_instance_id=ai1.id, data_asset_id=asset1.id,
        access_type="read"
    )
    db.add(rel1)
    db.flush()

    yield db, org, vendor, ai1, ai2, asset1
    db.close()
    Base.metadata.drop_all(engine)


def test_concentration_detects_vendor_with_crown_jewels(db_setup):
    """Vendors with crown jewel access should have elevated concentration score."""
    db, org, vendor, ai1, ai2, asset1 = db_setup
    engine = SupplierRiskEngine(db, org.id)
    results = engine.calculate_concentration_risk()
    assert len(results) >= 1
    v_result = next((r for r in results if r["vendor_id"] == vendor.id), None)
    assert v_result is not None
    assert v_result["crown_jewels_count"] >= 1
    assert v_result["concentration_score"] >= 25.0


def test_concentration_score_within_bounds(db_setup):
    """Concentration score must be between 0 and 100."""
    db, org, vendor, _, _, _ = db_setup
    engine = SupplierRiskEngine(db, org.id)
    results = engine.calculate_concentration_risk()
    for r in results:
        assert 0.0 <= r["concentration_score"] <= 100.0


def test_failure_impact_simulation_crown_jewel(db_setup):
    """Failure impact simulation must identify crown jewel exposure."""
    db, org, vendor, _, _, asset1 = db_setup
    engine = SupplierRiskEngine(db, org.id)
    result = engine.simulate_single_supplier_failure(vendor.id)
    assert "affected_applications" in result
    assert "potential_impact_score" in result
    assert result["potential_impact_score"] >= 0.0
    assert result["potential_impact_score"] <= 100.0
    assert len(result["affected_crown_jewels"]) >= 1


def test_failure_impact_missing_vendor(db_setup):
    """Missing vendor ID must return error dict without raising exception."""
    db, org, _, _, _, _ = db_setup
    engine = SupplierRiskEngine(db, org.id)
    result = engine.simulate_single_supplier_failure("non-existent-vendor-id")
    assert "error" in result
