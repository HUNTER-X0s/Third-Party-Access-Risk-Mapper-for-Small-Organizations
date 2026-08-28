"""
Phase 2 Demo Scenario Verification Script
Tests the central question: "What happens if GitHub is compromised?"

Authoritative blast radius values (graph-state derived, v2.1.0):
  Current      : 75.0 / 100 (High)
  Post-remediation (revoke org_admin + repo_write): 50.0 / 100 (Medium)
  Reduction    : 25.0 (automatically derived)
"""

from fastapi.testclient import TestClient
from app.main import app

# Authoritative expected values
EXPECTED_BR_BEFORE    = 75.0
EXPECTED_BR_AFTER     = 50.0
EXPECTED_BR_REDUCTION = 25.0

def run_phase2_demo_verification():
    client = TestClient(app)
    print("=" * 60)
    print("STARTING PHASE 2 DEMO SCENARIO VERIFICATION")
    print("QUESTION: What happens if GitHub is compromised?")
    print("=" * 60)

    # 1. Attack Path Discovery
    res_paths = client.get("/api/v1/graph/paths")
    assert res_paths.status_code == 200
    paths = res_paths.json()
    assert len(paths) >= 1
    
    gh_path = next(p for p in paths if "GitHub" in p["entry_application"])
    print(f"Step 1: Discovered Attack Path:")
    print(f"  Entry: {gh_path['entry_application']} -> Scope: organization_admin -> Target: {gh_path['target_data_asset']} (Crown Jewel: {gh_path['is_crown_jewel_targeted']})")
    print(f"  Impacted Process: {gh_path['business_process_impacted']}")
    print(f"  Path Risk Score: {gh_path['path_risk_score']} pts | Confidence: {gh_path['confidence_percentage']}% ({gh_path['verification_state']})")

    # 2. Application Blast Radius
    res_br = client.get(f"/api/v1/graph/blast-radius/{gh_path['entry_app_id']}")
    assert res_br.status_code == 200
    br = res_br.json()
    print(f"\nStep 2: Calculated Blast Radius:")
    print(f"  Blast Radius Score: {br['blast_radius_score']} / 100 ({br['score_severity']})")
    print(f"  Reachable Data Assets: {br['affected_data_assets_count']} | Crown Jewels: {br['affected_crown_jewels_count']}")
    print(f"  Impacted Processes: {br['affected_business_processes_count']} | Exposed Users: {br['affected_users_count']}")

    # 3. Crown Jewel Reachability Query
    res_cj = client.get("/api/v1/graph/reachability/crown-jewels")
    assert res_cj.status_code == 200
    cj_reach = res_cj.json()
    print(f"\nStep 3: Crown Jewel Reachability:")
    for r in cj_reach:
        print(f"  - App: {r['application_name']} ({r['app_risk_severity']}) -> Asset: {r['data_asset_name']} (Access: {r['access_type']})")

    # 4. Minimum Effective Remediation Optimization
    res_findings = client.get(f"/api/v1/applications/{gh_path['entry_app_id']}/findings")
    assert res_findings.status_code == 200
    findings = res_findings.json()
    crit_finding = findings[0]
    
    res_opt = client.get(f"/api/v1/findings/{crit_finding['id']}/remediation-analysis")
    assert res_opt.status_code == 200
    opt = res_opt.json()
    print(f"\nStep 4: Minimum Effective Remediation Recommendation:")
    print(f"  Target Threshold: Risk < {opt['target_threshold_score']}")
    print(f"  Current Risk: {opt['current_score']} -> Predicted Residual: {opt['predicted_residual_score']} ({opt['predicted_severity']})")
    print(f"  Recommended Minimal Revocations: {opt['recommended_minimal_revocations']}")
    print(f"  Attack Paths Reduction: {opt['attack_paths_before']} -> {opt['attack_paths_after']}")
    print(f"  Blast Radius Reduction: {opt['blast_radius_before']} -> {opt['blast_radius_after']} (reduction = {opt.get('blast_radius_reduction', 'N/A')})")
    print(f"  Warning: {opt['simulation_warning']}")

    # Verify authoritative blast radius values (graph-state derived)
    assert br['blast_radius_score'] == EXPECTED_BR_BEFORE, \
        f"blast_radius_before: expected {EXPECTED_BR_BEFORE}, got {br['blast_radius_score']}"
    assert opt['blast_radius_before'] == EXPECTED_BR_BEFORE, \
        f"optimizer blast_radius_before: expected {EXPECTED_BR_BEFORE}, got {opt['blast_radius_before']}"
    assert opt['blast_radius_after'] == EXPECTED_BR_AFTER, \
        f"optimizer blast_radius_after: expected {EXPECTED_BR_AFTER}, got {opt['blast_radius_after']}"
    assert opt.get('blast_radius_reduction') == EXPECTED_BR_REDUCTION, \
        f"blast_radius_reduction: expected {EXPECTED_BR_REDUCTION}, got {opt.get('blast_radius_reduction')}"
    assert opt['is_target_achieved'] is True

    print("\nPhase 2 Demo Scenario verification passed 100%!")
    print("=" * 60)

if __name__ == "__main__":
    run_phase2_demo_verification()
