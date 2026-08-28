"""
Test: Supply chain graph endpoint.
Validates that GET /graph/supply-chain returns correct node/edge structure.
"""
import pytest


def test_supply_chain_graph_returns_nodes_and_edges(client, db_session):
    """GET /graph/supply-chain must return nodes and edges lists."""
    login = client.post("/api/v1/auth/login", json={"email": "admin@anurag.tech", "password": "DemoPass123!"})
    token = login.cookies.get("access_token")

    resp = client.get("/api/v1/graph/supply-chain", cookies={"access_token": token})
    assert resp.status_code == 200
    data = resp.json()
    assert "nodes" in data
    assert "edges" in data


def test_supply_chain_graph_contains_org_node(client, db_session):
    """Graph must include an organization node."""
    login = client.post("/api/v1/auth/login", json={"email": "admin@anurag.tech", "password": "DemoPass123!"})
    token = login.cookies.get("access_token")

    resp = client.get("/api/v1/graph/supply-chain", cookies={"access_token": token})
    data = resp.json()
    org_nodes = [n for n in data.get("nodes", []) if n.get("type") == "organization"]
    assert len(org_nodes) >= 1


def test_supply_chain_graph_vendor_nodes_have_tier(client, db_session):
    """Vendor nodes must contain tier information."""
    login = client.post("/api/v1/auth/login", json={"email": "admin@anurag.tech", "password": "DemoPass123!"})
    token = login.cookies.get("access_token")

    resp = client.get("/api/v1/graph/supply-chain", cookies={"access_token": token})
    data = resp.json()
    vendor_nodes = [n for n in data.get("nodes", []) if n.get("type") == "vendor"]
    for vn in vendor_nodes:
        assert "tier" in vn.get("data", {})
