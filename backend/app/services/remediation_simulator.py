"""
Remediation Simulator Service
Simulates risk reduction by pre-calculating score changes if excess permissions are revoked.
Pure logic, zero real external mutations.
"""

from typing import Dict, Any, List
from app.services.risk_engine import calculate_risk

def simulate_remediation(
    current_risk_input: Dict[str, Any],
    proposed_revoked_scopes: List[str],
    remaining_scopes: List[str]
) -> Dict[str, Any]:
    """
    Recalculates risk score with excess scopes removed.
    Returns current_score, simulated_score, risk_reduction_delta, percentage_reduction.
    """
    # Recalculate excess ratio assuming proposed scopes are removed
    current_excess_ratio = current_risk_input.get("excess_ratio", 0.5)
    total_scopes = len(proposed_revoked_scopes) + len(remaining_scopes)
    
    new_excess_ratio = 0.0 if len(remaining_scopes) > 0 else 0.0
    
    # Recalculate max scope severity after revocation
    new_max_severity = "Low" if len(remaining_scopes) > 0 else "Info"
    for scope in remaining_scopes:
        from app.services.scope_normalizer import normalize_scope
        _, _, _, sev = normalize_scope(scope)
        if sev == "Critical":
            new_max_severity = "Critical"
        elif sev == "High" and new_max_severity != "Critical":
            new_max_severity = "High"
        elif sev == "Medium" and new_max_severity not in ("Critical", "High"):
            new_max_severity = "Medium"
            
    simulated_input = dict(current_risk_input)
    simulated_input["max_scope_severity"] = new_max_severity
    simulated_input["excess_ratio"] = new_excess_ratio
    simulated_input["in_attack_path"] = False  # Revoking excess breaks attack path
    
    current_result = calculate_risk(**current_risk_input)
    simulated_result = calculate_risk(**simulated_input)
    
    current_score = current_result["overall_score"]
    simulated_score = simulated_result["overall_score"]
    delta = round(max(0.0, current_score - simulated_score), 1)
    pct_reduction = round((delta / current_score * 100.0) if current_score > 0 else 0.0, 1)
    
    return {
        "is_simulation": True,
        "mode_label": "SIMULATION ONLY",
        "current_score": current_score,
        "current_severity": current_result["severity"],
        "simulated_score": simulated_score,
        "simulated_severity": simulated_result["severity"],
        "risk_reduction_delta": delta,
        "percentage_reduction": pct_reduction,
        "revoked_scopes_count": len(proposed_revoked_scopes),
        "simulated_result": simulated_result
    }
