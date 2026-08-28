"""
backend/tests/test_phase9_performance_resilience.py
Phase 9 Synthetic Performance Benchmarking & Failure Injection Resilience Tests.
Measures latency on graph traversal, risk calculation, search, and verifies database rollback behavior.
"""
import pytest
import time
from app.services.risk_engine import calculate_risk
from app.services.graph_engine import GraphEngine
from app.services.blast_radius_engine import BlastRadiusCalculator
from app.services.supplier_risk_engine import SupplierRiskEngine
from app.models import Organization, ApplicationInstance


def test_performance_risk_engine_batch_throughput():
    """
    Measures throughput for RiskEngine v1.5.0.
    1,000 risk evaluations must execute in < 500ms (deterministic CPU engine).
    """
    start_time = time.time()
    for _ in range(1000):
        calculate_risk(
            max_scope_severity="High",
            excess_ratio=0.5,
            max_data_sensitivity=4,
            system_criticality=4,
            vendor_trust_score=75.0,
            is_shadow=False,
            in_attack_path=True,
            is_crown_jewel_exposed=True
        )
    elapsed = (time.time() - start_time) * 1000  # in ms
    assert elapsed < 500.0  # Must be well under 500ms for 1,000 evaluations (p99 < 0.5ms)


def test_performance_graph_traversal_latency(db_session):
    """
    Measures latency for GraphEngine attack path discovery and reachability analysis.
    Must complete in < 150ms on seeded dataset.
    """
    org = db_session.query(Organization).first()
    if org:
        engine = GraphEngine(db_session, org.id)
        start_time = time.time()
        paths = engine.discover_potential_attack_paths()
        elapsed = (time.time() - start_time) * 1000
        assert elapsed < 150.0
        assert isinstance(paths, list)


def test_failure_injection_database_transaction_rollback(db_session):
    """
    Failure Injection: Simulates an exception during a multi-step database operation.
    Verifies that the transaction cleanly rolls back and no orphaned or partial records persist.
    """
    initial_apps_count = db_session.query(ApplicationInstance).count()

    try:
        # Create an invalid record that triggers a constraint violation
        invalid_app = ApplicationInstance(
            id="fault-injection-app-id",
            organization_id="non-existent-org-uuid",
            display_name=None  # NOT NULL violation
        )
        db_session.add(invalid_app)
        db_session.flush()
    except Exception:
        db_session.rollback()

    # Total apps count must remain exactly as before
    current_apps_count = db_session.query(ApplicationInstance).count()
    assert current_apps_count == initial_apps_count
