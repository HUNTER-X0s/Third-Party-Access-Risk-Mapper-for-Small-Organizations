import pytest
from app.models import ApplicationInstance, RiskFinding, PermissionGrant
from app.services.scope_normalizer import normalize_scope
from app.services.purpose_evaluator import evaluate_excess_permissions, evaluate_purpose_data_mismatch
from app.services.evidence_engine import compute_payload_hash
from app.services.risk_engine import calculate_risk, CALIBRATION_VECTORS
from app.services.remediation_simulator import simulate_remediation

# --- 1. DOMAIN & SERVICE UNIT TESTS ---

def test_scope_normalizer():
    canonical, name, desc, sev = normalize_scope("organization_admin")
    assert canonical == "ADMIN"
    assert sev == "Critical"
    
    canonical_write, _, _, sev_write = normalize_scope("Customer.Write")
    assert canonical_write == "WRITE"
    assert sev_write == "High"

def test_purpose_evaluator_excess_detection():
    granted = ["repo_read", "repo_write", "organization_admin"]
    required = ["READ"]
    res = evaluate_excess_permissions(granted, required)
    assert res["is_excess_detected"] is True
    assert res["excess_count"] == 2

def test_purpose_data_mismatch():
    expected = ["Customer Email"]
    actual = ["Customer Email", "Customer Address", "Payment History"]
    res = evaluate_purpose_data_mismatch(expected, actual)
    assert res["is_mismatch"] is True
    assert "Payment History" in res["unexpected_data_categories"]

def test_evidence_engine_sha256_hash():
    payload = {"org": "Anurag", "status": "OK"}
    h1 = compute_payload_hash(payload)
    h2 = compute_payload_hash(payload)
    assert h1 == h2
    assert len(h1) == 64

def test_risk_engine_calibration_vectors():
    vec_low = CALIBRATION_VECTORS["VEC-LOW"]
    res_low = calculate_risk(**vec_low["inputs"])
    assert res_low["severity"] == vec_low["expected_severity"]
    assert vec_low["expected_score_range"][0] <= res_low["overall_score"] <= vec_low["expected_score_range"][1]

    vec_crit = CALIBRATION_VECTORS["VEC-CRITICAL"]
    res_crit = calculate_risk(**vec_crit["inputs"])
    assert res_crit["severity"] == vec_crit["expected_severity"]
    assert vec_crit["expected_score_range"][0] <= res_crit["overall_score"] <= vec_crit["expected_score_range"][1]

def test_risk_engine_monotonicity():
    base_input = {
        "max_scope_severity": "Medium",
        "excess_ratio": 0.20,
        "max_data_sensitivity": 3,
        "system_criticality": 3,
        "vendor_trust_score": 70.0
    }
    res_base = calculate_risk(**base_input)
    
    escalated_input = dict(base_input)
    escalated_input["max_data_sensitivity"] = 5
    res_escalated = calculate_risk(**escalated_input)
    
    assert res_escalated["overall_score"] >= res_base["overall_score"]

def test_remediation_simulator():
    current_input = {
        "max_scope_severity": "Critical",
        "excess_ratio": 0.66,
        "max_data_sensitivity": 5,
        "system_criticality": 5,
        "vendor_trust_score": 50.0,
        "in_attack_path": True
    }
    sim_res = simulate_remediation(current_input, ["organization_admin", "repo_write"], ["repo_read"])
    assert sim_res["is_simulation"] is True
    assert sim_res["mode_label"] == "SIMULATION ONLY"
    assert sim_res["simulated_score"] < sim_res["current_score"]
    assert sim_res["risk_reduction_delta"] > 0.0

# --- 2. API ENDPOINT INTEGRATION TESTS ---

def test_api_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert data["organization"] == "Anurag Technologies"

def test_api_dashboard(client):
    res = client.get("/api/v1/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert data["organization_name"] == "Anurag Technologies"
    assert data["total_applications"] == 9
    assert data["critical_findings_count"] >= 1

def test_api_applications(client):
    res = client.get("/api/v1/applications")
    assert res.status_code == 200
    apps = res.json()
    assert len(apps) == 9
    
    gh_app = next(a for a in apps if "GitHub" in a["display_name"])
    assert gh_app["risk_severity"] == "Critical"
    
    res_detail = client.get(f"/api/v1/applications/{gh_app['id']}")
    assert res_detail.status_code == 200
    
    res_perms = client.get(f"/api/v1/applications/{gh_app['id']}/permissions")
    assert res_perms.status_code == 200
    perms = res_perms.json()
    assert any(p["raw_scope"] == "organization_admin" and p["is_excess"] for p in perms)

def test_api_findings_and_simulation(client):
    res_findings = client.get("/api/v1/findings")
    assert res_findings.status_code == 200
    findings = res_findings.json()
    assert len(findings) >= 2
    
    crit_finding = next(f for f in findings if f["severity"] == "Critical")
    finding_id = crit_finding["id"]
    
    sim_payload = {"revoked_scopes": ["organization_admin", "repo_write"]}
    res_sim = client.post(f"/api/v1/findings/{finding_id}/simulate-remediation", json=sim_payload)
    assert res_sim.status_code == 200
    sim_data = res_sim.json()
    assert sim_data["is_simulation"] is True
    assert sim_data["mode_label"] == "SIMULATION ONLY"
    assert sim_data["simulated_score"] < sim_data["current_score"]

def test_api_graph(client):
    res = client.get("/api/v1/graph")
    assert res.status_code == 200
    graph_data = res.json()
    assert len(graph_data["nodes"]) >= 10
    assert len(graph_data["edges"]) >= 8

# --- 3. NEGATIVE TESTING ---

def test_negative_invalid_application_id(client):
    res = client.get("/api/v1/applications/invalid-uuid-999")
    assert res.status_code == 404

def test_negative_invalid_finding_simulation(client):
    res = client.post("/api/v1/findings/invalid-uuid-999/simulate-remediation", json={"revoked_scopes": []})
    assert res.status_code == 404
