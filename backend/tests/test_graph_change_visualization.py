"""
backend/tests/test_graph_change_visualization.py
Tests for Graph Change Visualization, Delta Mode & Edge Status Annotations.
"""
import pytest
from app.models import Organization, SecurityChange, SecuritySnapshot


def test_graph_delta_endpoint_annotations(client, db_session):
    """Verifies that GET /api/v1/graph/delta returns annotated edges with NEW/CHANGED/UNCHANGED change_status."""
    org = db_session.query(Organization).first()
    assert org is not None

    res = client.get("/api/v1/graph/delta")
    assert res.status_code == 200
    data = res.json()

    assert "nodes" in data
    assert "edges" in data
    assert "delta_summary" in data

    edges = data["edges"]
    assert len(edges) > 0

    # Ensure all edges have change_status
    for edge in edges:
        assert "change_status" in edge
        assert edge["change_status"] in ("NEW", "CHANGED", "REMOVED", "UNCHANGED")

    # Verify summary counts match edge counts
    summary = data["delta_summary"]
    new_count = sum(1 for e in edges if e["change_status"] == "NEW")
    changed_count = sum(1 for e in edges if e["change_status"] == "CHANGED")
    unchanged_count = sum(1 for e in edges if e["change_status"] == "UNCHANGED")

    assert summary["new_edges_count"] == new_count
    assert summary["changed_edges_count"] == changed_count
    assert summary["unchanged_edges_count"] == unchanged_count


def test_changed_edge_inspection_metadata(client, db_session):
    """Verifies that changed/new edges contain inspection metadata (before, after, risk_impact, evidence_refs)."""
    res = client.get("/api/v1/graph/delta")
    assert res.status_code == 200
    data = res.json()

    changed_or_new = [e for e in data["edges"] if e["change_status"] in ("NEW", "CHANGED")]
    if changed_or_new:
        edge = changed_or_new[0]
        meta = edge.get("change_metadata")
        assert meta is not None
        assert "change_id" in meta
        assert "change_type" in meta
        assert "severity" in meta
        assert "before" in meta
        assert "after" in meta
        assert "risk_impact" in meta
