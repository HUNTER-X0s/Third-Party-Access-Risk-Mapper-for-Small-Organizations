"""
Blast Radius Engine Regression Tests (v2.1.0)

These tests pin authoritative values derived from the graph/domain state.
All values are computed by BlastRadiusCalculator from live DB records —
no hardcoded proportions or static fallbacks.

Authoritative values (Phase 2 seed, GitHub Production Sync):
  Current blast radius          : 75.0 / 100
  Factor breakdown              : CJ=30 + Asset=10 + BizProc=20 + Users=15 = 75
  Post-remediation (revoke admin+write) : 50.0 / 100
  Factor breakdown (damping 0.5): CJ=15 + Asset=10 + BizProc=10 + Users=15 = 50
  Reduction (auto-derived)      : 75.0 - 50.0 = 25.0
"""

import pytest
from app.models import Organization, ApplicationInstance, RiskFinding
from app.services.blast_radius_engine import BlastRadiusCalculator
from app.services.remediation_optimizer import RemediationOptimizer

# ── Scope constants matching seed data ────────────────────────────────────────
EXCESS_SCOPES = ["organization_admin", "repo_write"]
REMAINING_SCOPE = "repo_read"

# ── Authoritative expected values ─────────────────────────────────────────────
EXPECTED_CURRENT_SCORE   = 75.0
EXPECTED_POST_REM_SCORE  = 50.0
EXPECTED_REDUCTION       = 25.0   # EXPECTED_CURRENT_SCORE - EXPECTED_POST_REM_SCORE


# ── Helper ────────────────────────────────────────────────────────────────────

def _get_github_app(db):
    return db.query(ApplicationInstance).filter(
        ApplicationInstance.display_name == "GitHub Production Sync"
    ).first()


# ── Requirement 1: Current blast radius = 75.0 with correct factor sum ────────

def test_current_blast_radius_is_75(db_session):
    """Factor breakdown must sum to exactly 75.0 from graph state."""
    org = db_session.query(Organization).first()
    app = _get_github_app(db_session)
    assert app is not None

    calc = BlastRadiusCalculator(db_session, org.id)
    res  = calc.calculate_application_blast_radius(app.id)

    assert res["blast_radius_score"] == EXPECTED_CURRENT_SCORE, (
        f"Expected {EXPECTED_CURRENT_SCORE}, got {res['blast_radius_score']}"
    )
    # Factor sum must equal the final score (no rounding drift > 0.05)
    factor_sum = sum(f["delta"] for f in res["factors"])
    assert abs(factor_sum - EXPECTED_CURRENT_SCORE) < 0.05, (
        f"Factor sum {factor_sum} does not equal score {EXPECTED_CURRENT_SCORE}"
    )
    # Expected individual factors
    assert res["affected_crown_jewels_count"] == 1
    assert res["affected_data_assets_count"] == 1
    assert res["affected_business_processes_count"] >= 1
    assert res["affected_users_count"] == 28
    assert res["max_permission_severity"] == "Critical"
    assert res["severity_damping"] == 1.0
    assert res["state"] == "CURRENT"


def test_current_blast_radius_factor_names(db_session):
    """Verify individual factor deltas match model specification."""
    org = db_session.query(Organization).first()
    app = _get_github_app(db_session)
    calc = BlastRadiusCalculator(db_session, org.id)
    res  = calc.calculate_application_blast_radius(app.id)
    deltas = {f["name"]: f["delta"] for f in res["factors"]}

    assert deltas.get("Reaches 1 Crown Jewel Data Asset") == 30.0
    assert deltas.get("Reaches 1 Sensitive Data Asset") == 10.0
    # Business process factor (may appear as "Impacts N Critical Business Processes")
    bp_delta = next((v for k, v in deltas.items() if "Business Processes" in k), None)
    assert bp_delta == 20.0, f"Business process delta should be 20.0, got {bp_delta}"
    # Users factor
    user_delta = next((v for k, v in deltas.items() if "User Accounts" in k), None)
    assert user_delta == 15.0, f"Users delta should be 15.0, got {user_delta}"


# ── Requirement 2: Post-remediation blast radius = 50.0 from graph state ──────

def test_post_remediation_blast_radius_is_50(db_session):
    """
    After revoking organization_admin + repo_write, only repo_read (Low) remains.
    Severity damping of 0.5 is applied to crown-jewel and business-process factors.
    Graph-state derived score must equal 50.0.
    """
    org = db_session.query(Organization).first()
    app = _get_github_app(db_session)
    calc = BlastRadiusCalculator(db_session, org.id)

    res = calc.calculate_post_remediation_blast_radius(app.id, EXCESS_SCOPES)

    assert res["blast_radius_score"] == EXPECTED_POST_REM_SCORE, (
        f"Expected post-remediation score {EXPECTED_POST_REM_SCORE}, got {res['blast_radius_score']}"
    )
    assert res["max_permission_severity"] == "Low", (
        f"After revoking admin+write, max severity should be Low, got {res['max_permission_severity']}"
    )
    assert res["severity_damping"] == 0.5
    assert REMAINING_SCOPE in res["remaining_scopes"]
    assert res["state"] == "POST_REMEDIATION"

    # Factor sum check
    factor_sum = sum(f["delta"] for f in res["factors"])
    assert abs(factor_sum - EXPECTED_POST_REM_SCORE) < 0.05, (
        f"Post-remediation factor sum {factor_sum} != {EXPECTED_POST_REM_SCORE}"
    )


def test_post_remediation_factor_damping(db_session):
    """Crown-jewel and biz-process factors are halved when severity drops to Low."""
    org = db_session.query(Organization).first()
    app = _get_github_app(db_session)
    calc = BlastRadiusCalculator(db_session, org.id)
    res  = calc.calculate_post_remediation_blast_radius(app.id, EXCESS_SCOPES)
    deltas = {f["name"]: f["delta"] for f in res["factors"]}

    # Crown Jewel: 30 * 0.5 = 15
    assert deltas.get("Reaches 1 Crown Jewel Data Asset") == 15.0
    # Asset: unchanged at 10
    assert deltas.get("Reaches 1 Sensitive Data Asset") == 10.0
    # Business Process: 20 * 0.5 = 10
    bp_delta = next((v for k, v in deltas.items() if "Business Processes" in k), None)
    assert bp_delta == 10.0, f"BizProcess factor should be 10.0 post-remediation, got {bp_delta}"
    # Users: unchanged at 15
    user_delta = next((v for k, v in deltas.items() if "User Accounts" in k), None)
    assert user_delta == 15.0


# ── Requirement 3: Reduction auto-derived ─────────────────────────────────────

def test_blast_radius_reduction_auto_derived(db_session):
    """
    Reduction must equal before − after without any hardcoded constant.
    This test computes both sides independently and checks the arithmetic.
    """
    org = db_session.query(Organization).first()
    app = _get_github_app(db_session)
    calc = BlastRadiusCalculator(db_session, org.id)

    before = calc.calculate_application_blast_radius(app.id)["blast_radius_score"]
    after  = calc.calculate_post_remediation_blast_radius(app.id, EXCESS_SCOPES)["blast_radius_score"]
    reduction = round(before - after, 1)

    assert before == EXPECTED_CURRENT_SCORE
    assert after  == EXPECTED_POST_REM_SCORE
    assert reduction == EXPECTED_REDUCTION, (
        f"Auto-derived reduction {reduction} != {EXPECTED_REDUCTION}"
    )


# ── Requirement 4: Optimizer calls real engine, not proportional arithmetic ───

def test_optimizer_calls_graph_engine(db_session):
    """Source code inspection: optimizer must call calculate_post_remediation_blast_radius."""
    import inspect
    src = inspect.getsource(RemediationOptimizer.calculate_minimum_effective_remediation)
    assert "calculate_post_remediation_blast_radius" in src, (
        "FAIL: optimizer does not call calculate_post_remediation_blast_radius"
    )
    assert "br_before_score * " not in src, (
        "FAIL: optimizer still contains proportional blast radius arithmetic"
    )


# ── Requirement 5: Optimizer output matches direct engine output ───────────────

def test_optimizer_blast_radius_matches_engine(db_session):
    """blast_radius_before/after in optimizer output must match BlastRadiusCalculator."""
    org = db_session.query(Organization).first()
    app = _get_github_app(db_session)
    finding = db_session.query(RiskFinding).filter(
        RiskFinding.application_instance_id == app.id
    ).first()
    assert finding is not None

    calc = BlastRadiusCalculator(db_session, org.id)
    br_before = calc.calculate_application_blast_radius(app.id)["blast_radius_score"]
    br_after  = calc.calculate_post_remediation_blast_radius(app.id, EXCESS_SCOPES)["blast_radius_score"]

    opt = RemediationOptimizer(db_session, org.id)
    result = opt.calculate_minimum_effective_remediation(finding.id, target_max_score=55.0)

    assert result["blast_radius_before"] == br_before
    assert result["blast_radius_after"]  == br_after
    assert result["blast_radius_reduction"] == round(br_before - br_after, 1)


# ── Requirement 6a: Target 55 is achievable ───────────────────────────────────

def test_target_55_is_achievable(db_session):
    """
    With target=55.0 and simulated residual=53.6, the optimizer must report
    is_target_achieved=True. 53.6 <= 55.0 must be strict boolean.
    """
    org = db_session.query(Organization).first()
    app = _get_github_app(db_session)
    finding = db_session.query(RiskFinding).filter(
        RiskFinding.application_instance_id == app.id
    ).first()

    opt = RemediationOptimizer(db_session, org.id)
    result = opt.calculate_minimum_effective_remediation(finding.id, target_max_score=55.0)

    assert result["is_target_achieved"] is True
    assert result["predicted_residual_score"] <= 55.0
    assert "BEST EFFORT" not in result["recommended_candidate_name"]


# ── Requirement 6b: Target 50 is not achievable ───────────────────────────────

def test_target_50_not_achievable(db_session):
    """
    With target=50.0 and simulated residual=53.6, the optimizer must report
    is_target_achieved=False and include BEST EFFORT in the candidate label.
    """
    org = db_session.query(Organization).first()
    app = _get_github_app(db_session)
    finding = db_session.query(RiskFinding).filter(
        RiskFinding.application_instance_id == app.id
    ).first()

    opt = RemediationOptimizer(db_session, org.id)
    result = opt.calculate_minimum_effective_remediation(finding.id, target_max_score=50.0)

    assert result["is_target_achieved"] is False
    assert result["predicted_residual_score"] > 50.0
    assert "BEST EFFORT" in result["recommended_candidate_name"]


# ── Requirement 6c: Impossible target (40) is not achievable ──────────────────

def test_impossible_target_40(db_session):
    """
    With target=40.0 (below all candidate simulated scores), optimizer must
    report is_target_achieved=False. NEVER silently change the target.
    """
    org = db_session.query(Organization).first()
    app = _get_github_app(db_session)
    finding = db_session.query(RiskFinding).filter(
        RiskFinding.application_instance_id == app.id
    ).first()

    opt = RemediationOptimizer(db_session, org.id)
    result = opt.calculate_minimum_effective_remediation(finding.id, target_max_score=40.0)

    assert result["is_target_achieved"] is False
    assert result["target_threshold_score"] == 40.0, (
        "Optimizer must NOT silently change the target threshold"
    )
    assert result["predicted_residual_score"] > 40.0
    assert "BEST EFFORT" in result["recommended_candidate_name"]


# ── Existing tests ─────────────────────────────────────────────────────────────

def test_blast_radius_invalid_application(db_session):
    org = db_session.query(Organization).first()
    calc = BlastRadiusCalculator(db_session, org.id)
    res = calc.calculate_application_blast_radius("invalid-app-id-999")
    assert "error" in res
