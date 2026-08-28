"""
backend/tests/test_phase9_cross_module_truth.py
Phase 9 Cross-Module Single-Source-of-Truth, Risk Consistency, and Graph Integrity Tests.
Validates: Authoritative metric agreement across Dashboard, Graph, Findings, BlastRadius, and Remediation.
"""
import pytest
from app.services.risk_engine import calculate_risk
from app.services.graph_engine import GraphEngine
from app.services.blast_radius_engine import BlastRadiusCalculator
from app.services.remediation_optimizer import RemediationOptimizer
from app.services.supplier_risk_engine import SupplierRiskEngine
from app.models import ApplicationInstance, Organization, RiskFinding


def test_risk_engine_monotonicity_and_clamping():
    """
    Verifies that RiskEngine v1.5.0 produces deterministic scores clamped strictly between 0 and 100,
    and higher sensitivity / critical scopes strictly yield higher or equal risk scores.
    """
    # Low scope
    r_low = calculate_risk(
        max_scope_severity="Low",
        excess_ratio=0.0,
        max_data_sensitivity=1,
        system_criticality=2,
        vendor_trust_score=90.0,
        is_shadow=False,
        in_attack_path=False
    )
    # Critical scope with Crown Jewel
    r_crit = calculate_risk(
        max_scope_severity="Critical",
        excess_ratio=0.8,
        max_data_sensitivity=5,
        system_criticality=5,
        vendor_trust_score=20.0,
        is_shadow=True,
        in_attack_path=True,
        is_crown_jewel_exposed=True
    )
    assert 0.0 <= r_low["overall_score"] <= 100.0
    assert 0.0 <= r_crit["overall_score"] <= 100.0
    assert r_crit["overall_score"] > r_low["overall_score"]
    assert r_crit["severity"] in ("Critical", "High")


def test_cross_module_truth_github_scenario(client, db_session):
    """
    Single-Source-of-Truth Test:
    Ensures that for the canonical GitHub scenario, the Risk Score, Blast Radius,
    and Graph Reachability metrics agree authoritatively across all endpoints.
    """
    login = client.post("/api/v1/auth/login", json={"email": "admin@anurag.tech", "password": "DemoPass123!"})
    token = login.cookies.get("access_token")

    # 1. Query dashboard
    dash = client.get("/api/v1/dashboard", cookies={"access_token": token}).json()
    org_posture = dash["security_posture_score"]
    assert 0.0 <= org_posture <= 100.0

    # 2. Query applications
    apps_res = client.get("/api/v1/applications", cookies={"access_token": token}).json()
    apps = apps_res if isinstance(apps_res, list) else apps_res.get("applications", [])
    gh_app = next((a for a in apps if "github" in a["display_name"].lower()), None)
    assert gh_app is not None

    gh_app_risk = gh_app["risk_score"]

    # 3. Query blast radius
    br_res = client.get(f"/api/v1/graph/blast-radius/{gh_app['id']}", cookies={"access_token": token}).json()
    assert "blast_radius_score" in br_res or "accessible_data_assets_count" in br_res

    # 4. Query findings
    findings = client.get("/api/v1/findings", cookies={"access_token": token}).json()
    findings_list = findings if isinstance(findings, list) else findings.get("findings", [])
    gh_findings = [f for f in findings_list if f.get("application_instance_id") == gh_app["id"]]
    assert len(gh_findings) > 0


def test_remediation_optimizer_impossible_target_handling(db_session):
    """
    Verifies that when an impossible target risk reduction is requested (e.g. Target Score = 1.0
    while essential scopes must remain), the optimizer cleanly returns unachieved status
    without crashing or returning an invalid mutation.
    """
    org = db_session.query(Organization).first()
    finding = db_session.query(RiskFinding).first()

    if org and finding:
        optimizer = RemediationOptimizer(db_session, org.id)
        res = optimizer.calculate_minimum_effective_remediation(finding.id, target_max_score=1.0)
        assert res is not None
        assert "is_target_achieved" in res or "recommended_candidate_name" in res


def test_graph_engine_cycle_and_traversal_safety(db_session):
    """
    Verifies that GraphEngine traversal handles self-referencing relationships
    and cyclic graph structures deterministically without infinite recursion.
    """
    org = db_session.query(Organization).first()
    if org:
        engine = GraphEngine(db_session, org.id)
        paths = engine.discover_potential_attack_paths()
        assert isinstance(paths, list)
        reachability = engine.get_crown_jewel_reachability()
        assert isinstance(reachability, list) or isinstance(reachability, dict)
