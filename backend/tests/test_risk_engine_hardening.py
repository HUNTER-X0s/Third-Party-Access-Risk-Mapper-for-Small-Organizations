import pytest
from app.services.risk_engine import calculate_risk, score_to_severity, CALIBRATION_VECTORS

def test_risk_engine_calibration_vectors():
    for vec_name, vec in CALIBRATION_VECTORS.items():
        res = calculate_risk(**vec["inputs"])
        assert res["severity"] == vec["expected_severity"], f"Failed {vec_name} severity"
        min_s, max_s = vec["expected_score_range"]
        assert min_s <= res["overall_score"] <= max_s, f"Failed {vec_name} range: got {res['overall_score']}, expected [{min_s}, {max_s}]"

def test_scope_monotonicity():
    base = {
        "max_scope_severity": "Low",
        "excess_ratio": 0.0,
        "max_data_sensitivity": 1,
        "system_criticality": 1,
        "vendor_trust_score": 90.0
    }
    s_low = calculate_risk(**base)["overall_score"]
    
    base_med = dict(base, max_scope_severity="Medium")
    s_med = calculate_risk(**base_med)["overall_score"]
    
    base_high = dict(base, max_scope_severity="High")
    s_high = calculate_risk(**base_high)["overall_score"]
    
    base_crit = dict(base, max_scope_severity="Critical")
    s_crit = calculate_risk(**base_crit)["overall_score"]
    
    assert s_low <= s_med <= s_high <= s_crit

def test_data_sensitivity_monotonicity():
    base = {
        "max_scope_severity": "Medium",
        "excess_ratio": 0.2,
        "max_data_sensitivity": 1,
        "system_criticality": 2,
        "vendor_trust_score": 80.0
    }
    s1 = calculate_risk(**dict(base, max_data_sensitivity=1))["overall_score"]
    s3 = calculate_risk(**dict(base, max_data_sensitivity=3))["overall_score"]
    s5 = calculate_risk(**dict(base, max_data_sensitivity=5))["overall_score"]
    
    assert s1 <= s3 <= s5

def test_score_resolution_differentiation():
    # Verify risk engine distinguishes fine-grained high-risk scenarios (88, 92, 96, 100)
    scen_a = calculate_risk(max_scope_severity="High", excess_ratio=0.5, max_data_sensitivity=4, system_criticality=4, vendor_trust_score=60.0, in_attack_path=True)
    scen_b = calculate_risk(max_scope_severity="Critical", excess_ratio=0.6, max_data_sensitivity=4, system_criticality=4, vendor_trust_score=50.0, in_attack_path=True)
    scen_c = calculate_risk(max_scope_severity="Critical", excess_ratio=0.75, max_data_sensitivity=5, system_criticality=5, vendor_trust_score=20.0, is_shadow=True, in_attack_path=True, is_crown_jewel_exposed=True)
    
    assert scen_a["overall_score"] < scen_b["overall_score"] <= scen_c["overall_score"]

def test_boundary_clamping():
    # Test lower bound clamping
    res_min = calculate_risk("Info", 0.0, 1, 1, 100.0, False, False, False)
    assert 0.0 <= res_min["overall_score"] <= 100.0
    
    # Test upper bound clamping
    res_max = calculate_risk("Critical", 1.0, 5, 5, 0.0, True, True, True)
    assert res_max["overall_score"] == 100.0
