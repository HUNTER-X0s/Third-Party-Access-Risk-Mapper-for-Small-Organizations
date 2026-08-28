import pytest
from app.models import Organization, ApplicationInstance, RiskFinding, PermissionGrant, DataAsset
from app.services.graph_engine import GraphEngine
from app.services.blast_radius_engine import BlastRadiusCalculator
from app.services.snapshot_engine import SnapshotEngine
from app.services.remediation_optimizer import RemediationOptimizer

# Authoritative graph-state derived values (verified by verify_blast_radius.py)
CURRENT_BR    = 75.0
POST_REM_BR   = 50.0   # After revoking organization_admin + repo_write
BR_REDUCTION  = 25.0   # Automatically derived: CURRENT_BR - POST_REM_BR
EXCESS_SCOPES = ["organization_admin", "repo_write"]

def test_single_source_of_truth_consistency(client, db_session):
    """
    Verifies single source of truth across BlastRadiusCalculator and RemediationOptimizer:
    - blast_radius_before must match direct engine call (75.0)
    - blast_radius_after must match post-remediation engine call (50.0)
    - blast_radius_reduction must be automatically derived (25.0)
    - is_target_achieved must be strictly consistent with residual <= target
    """
    org = db_session.query(Organization).first()
    assert org is not None

    gh_app = db_session.query(ApplicationInstance).filter(
        ApplicationInstance.display_name == "GitHub Production Sync"
    ).first()
    assert gh_app is not None, "GitHub Production Sync must exist in seeded test data"

    # Direct engine calls (authoritative)
    br_calc = BlastRadiusCalculator(db_session, org.id)
    br_before_data = br_calc.calculate_application_blast_radius(gh_app.id)
    br_after_data  = br_calc.calculate_post_remediation_blast_radius(gh_app.id, EXCESS_SCOPES)

    assert br_before_data["blast_radius_score"] == CURRENT_BR
    assert br_after_data["blast_radius_score"]  == POST_REM_BR

    # Optimizer call
    finding = db_session.query(RiskFinding).filter(
        RiskFinding.application_instance_id == gh_app.id
    ).first()
    assert finding is not None

    optimizer = RemediationOptimizer(db_session, org.id)
    rem = optimizer.calculate_minimum_effective_remediation(finding.id, target_max_score=55.0)

    # blast_radius_before must match direct engine
    assert rem["blast_radius_before"] == CURRENT_BR, (
        f"blast_radius_before={rem['blast_radius_before']} != engine={CURRENT_BR}"
    )
    # blast_radius_after must match direct post-remediation engine call
    assert rem["blast_radius_after"] == POST_REM_BR, (
        f"blast_radius_after={rem['blast_radius_after']} != post-remediation engine={POST_REM_BR}"
    )
    # blast_radius_reduction must be auto-derived
    assert rem["blast_radius_reduction"] == BR_REDUCTION, (
        f"blast_radius_reduction={rem['blast_radius_reduction']} != {BR_REDUCTION}"
    )

    # is_target_achieved must be strictly consistent
    predicted_residual = rem["predicted_residual_score"]
    target_threshold   = rem["target_threshold_score"]
    is_achieved        = rem["is_target_achieved"]
    assert (predicted_residual <= target_threshold) == is_achieved
    assert is_achieved is True
    assert "BEST EFFORT" not in rem["recommended_candidate_name"]
    assert rem.get("optimizer_version") == "v2.1.0"
    assert "SIMULATION ONLY" in rem.get("simulation_warning", "")


def test_cross_module_data_integrity(db_session):
    """
    Verifies that GraphEngine attack paths reference the same underlying DataAsset
    records as the AccessRelationship layer, ensuring no fabricated graph edges.
    """
    org = db_session.query(Organization).first()

    # 1. Graph Engine potential attack paths
    graph_engine = GraphEngine(db_session, org.id)
    paths = graph_engine.discover_potential_attack_paths()
    assert len(paths) >= 1, "At least 1 potential attack path must be discovered"

    path = next(p for p in paths if "GitHub" in p["entry_application"])
    assert path["target_data_asset"] == "Source Code & Prop Algorithms"
    assert path["is_crown_jewel_targeted"] is True
    assert path["verification_state"] in ("VERIFIED", "PARTIALLY VERIFIED")

    # 2. Verify underlying DB Data Asset matches path target (no fabrication)
    asset = db_session.query(DataAsset).filter(
        DataAsset.name == path["target_data_asset"]
    ).first()
    assert asset is not None, "Target data asset must exist in database"
    assert asset.is_crown_jewel is True


def test_no_cross_tenant_blast_radius(client, db_session):
    """
    Verifies that BlastRadiusCalculator enforces strict organization_id filtering.
    App from Org A cannot be queried with Org B's organization_id.
    """
    from app.models import ApplicationInstance

    org = db_session.query(Organization).first()
    gh_app = db_session.query(ApplicationInstance).filter(
        ApplicationInstance.organization_id == org.id
    ).first()
    assert gh_app is not None

    # Calculate blast radius with correct org_id
    br_calc_correct = BlastRadiusCalculator(db_session, org.id)
    result_correct = br_calc_correct.calculate_application_blast_radius(gh_app.id)
    assert result_correct["blast_radius_score"] > 0

    # Calculate blast radius with wrong org_id (cross-tenant attempt)
    br_calc_wrong = BlastRadiusCalculator(db_session, "00000000-0000-0000-0000-000000000000")
    result_wrong = br_calc_wrong.calculate_application_blast_radius(gh_app.id)
    # Should return zero or error since app doesn't belong to that org
    assert result_wrong.get("blast_radius_score", 0) == 0 or result_wrong.get("error") is not None
