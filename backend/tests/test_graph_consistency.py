import pytest
from app.models import Organization, ApplicationInstance, DataAsset, AccessRelationship

def test_graph_data_consistency(client, db_session):
    org = db_session.query(Organization).first()
    db_apps = db_session.query(ApplicationInstance).filter(ApplicationInstance.organization_id == org.id).all()
    db_assets = db_session.query(DataAsset).filter(DataAsset.organization_id == org.id).all()
    db_rels = db_session.query(AccessRelationship).filter(AccessRelationship.organization_id == org.id).all()
    
    res = client.get("/api/v1/graph")
    assert res.status_code == 200
    graph = res.json()
    
    nodes = graph["nodes"]
    edges = graph["edges"]
    
    # 1. Verify Node Counts (1 Org node + N App nodes + M Asset nodes)
    expected_nodes_count = 1 + len(db_apps) + len(db_assets)
    assert len(nodes) == expected_nodes_count
    
    # 2. Verify Edge Counts (N Org-to-App edges + K App-to-Asset edges)
    expected_edges_count = len(db_apps) + len(db_rels)
    assert len(edges) == expected_edges_count
    
    # 3. Verify Edge Mapping 1-to-1 against AccessRelationship IDs
    db_rel_ids = {f"edge-rel-{r.id}" for r in db_rels}
    graph_rel_edge_ids = {e["id"] for e in edges if e["id"].startswith("edge-rel-")}
    assert db_rel_ids == graph_rel_edge_ids
