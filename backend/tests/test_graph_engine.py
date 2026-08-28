import pytest
from app.models import Organization, ApplicationInstance, DataAsset
from app.services.graph_engine import GraphEngine

def test_discover_potential_attack_paths(db_session):
    org = db_session.query(Organization).first()
    engine = GraphEngine(db_session, org.id)
    
    paths = engine.discover_potential_attack_paths()
    assert len(paths) >= 1
    
    gh_path = next(p for p in paths if p["entry_application"] == "GitHub Production Sync")
    assert gh_path["is_crown_jewel_targeted"] is True
    assert gh_path["target_data_asset"] == "Source Code & Prop Algorithms"
    assert gh_path["path_risk_score"] > 80.0
    assert len(gh_path["contributors"]) >= 3
    assert gh_path["verification_state"] in ("VERIFIED", "PARTIALLY VERIFIED")

def test_crown_jewel_reachability(db_session):
    org = db_session.query(Organization).first()
    engine = GraphEngine(db_session, org.id)
    
    reachability = engine.get_crown_jewel_reachability()
    assert len(reachability) >= 1
    
    cj_item = next(r for r in reachability if r["data_asset_name"] == "Source Code & Prop Algorithms")
    assert cj_item["application_name"] == "GitHub Production Sync"
    assert cj_item["access_type"] == "ADMIN"
    assert cj_item["has_excess_scopes"] is True

def test_graph_engine_tenant_isolation(db_session):
    org = db_session.query(Organization).first()
    engine_fake = GraphEngine(db_session, "fake-org-id-999")
    
    paths = engine_fake.discover_potential_attack_paths()
    assert len(paths) == 0
