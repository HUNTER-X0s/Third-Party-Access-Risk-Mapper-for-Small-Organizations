"""
Pure Python Deterministic Risk Engine v1.5.0
Calculates 5 distinct Risk Dimensions (TR, DER, BIR, VSR, APR) and computes Overall Risk Score (0-100).
Deterministic, fully reproducible, and traceable. ZERO AI logic inside this module.
"""

from typing import Dict, List, Any

RISK_ENGINE_VERSION = "v1.5.0"

# Calibration Test Vectors
CALIBRATION_VECTORS = {
    "VEC-LOW": {
        "expected_severity": "Low",
        "expected_score_range": (10, 25),
        "inputs": {
            "max_scope_severity": "Low",
            "excess_ratio": 0.0,
            "max_data_sensitivity": 1,
            "system_criticality": 2,
            "vendor_trust_score": 90.0,
            "is_shadow": False,
            "in_attack_path": False,
        }
    },
    "VEC-MEDIUM": {
        "expected_severity": "Medium",
        "expected_score_range": (42, 58),
        "inputs": {
            "max_scope_severity": "Medium",
            "excess_ratio": 0.25,
            "max_data_sensitivity": 3,
            "system_criticality": 3,
            "vendor_trust_score": 70.0,
            "is_shadow": False,
            "in_attack_path": False,
        }
    },
    "VEC-HIGH": {
        "expected_severity": "High",
        "expected_score_range": (68, 85),
        "inputs": {
            "max_scope_severity": "High",
            "excess_ratio": 0.60,
            "max_data_sensitivity": 4,
            "system_criticality": 4,
            "vendor_trust_score": 50.0,
            "is_shadow": False,
            "in_attack_path": True,
        }
    },
    "VEC-CRITICAL": {
        "expected_severity": "Critical",
        "expected_score_range": (88, 100),
        "inputs": {
            "max_scope_severity": "Critical",
            "excess_ratio": 0.75,
            "max_data_sensitivity": 5,
            "system_criticality": 5,
            "vendor_trust_score": 20.0,
            "is_shadow": True,
            "in_attack_path": True,
        }
    }
}

SEVERITY_SCORE_MAP = {
    "Critical": 100.0,
    "High": 75.0,
    "Medium": 50.0,
    "Low": 25.0,
    "Info": 10.0
}

def clamp(val: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    return max(min_val, min(max_val, val))

def score_to_severity(score: float) -> str:
    if score >= 85.0:
        return "Critical"
    elif score >= 65.0:
        return "High"
    elif score >= 40.0:
        return "Medium"
    elif score >= 15.0:
        return "Low"
    else:
        return "Info"

def calculate_risk(
    max_scope_severity: str,
    excess_ratio: float,
    max_data_sensitivity: int,  # 1 to 5
    system_criticality: int,   # 1 to 5
    vendor_trust_score: float, # 0 to 100
    is_shadow: bool = False,
    in_attack_path: bool = False,
    is_crown_jewel_exposed: bool = False
) -> Dict[str, Any]:
    """
    Computes the 5 dimensional scores and the overall risk score deterministically.
    """
    # 1. Technical Risk (TR) - Weight 0.30
    scope_sev_score = SEVERITY_SCORE_MAP.get(max_scope_severity, 50.0)
    tr = clamp(scope_sev_score * 0.60 + (excess_ratio * 100.0) * 0.40)
    
    # 2. Data Exposure Risk (DER) - Weight 0.25
    # Sensitivity 1-5 maps to 20, 40, 60, 85, 100
    der_map = {1: 20.0, 2: 40.0, 3: 60.0, 4: 85.0, 5: 100.0}
    der = der_map.get(max_data_sensitivity, 50.0)
    
    # 3. Business Impact Risk (BIR) - Weight 0.15
    bir_map = {1: 20.0, 2: 40.0, 3: 60.0, 4: 80.0, 5: 100.0}
    bir = bir_map.get(system_criticality, 50.0)
    if is_crown_jewel_exposed:
        bir = clamp(bir * 1.25)
        
    # 4. Vendor & Supply Chain Risk (VSR) - Weight 0.15
    # Low trust = high risk
    vsr = clamp(100.0 - vendor_trust_score)
    
    # 5. Attack Path Risk (APR) - Weight 0.15
    apr = 80.0 if in_attack_path else 20.0
    if is_crown_jewel_exposed and in_attack_path:
        apr = 100.0
        
    # Context Multiplier
    context_multiplier = 1.0
    if is_shadow:
        context_multiplier += 0.25
    if in_attack_path:
        context_multiplier += 0.15
    if is_crown_jewel_exposed:
        context_multiplier += 0.10
        
    context_multiplier = min(context_multiplier, 1.50)
    
    # Aggregation
    weighted_sum = (tr * 0.30) + (der * 0.25) + (bir * 0.15) + (vsr * 0.15) + (apr * 0.15)
    overall_score = round(clamp(weighted_sum * context_multiplier), 1)
    severity = score_to_severity(overall_score)
    
    # Factors Breakdown
    factors = [
        {
            "name": "Technical Risk & Scope Severity",
            "weight": 0.30,
            "current_value": round(tr, 1),
            "explanation": f"Highest scope severity is {max_scope_severity} with {int(excess_ratio * 100)}% excess permissions."
        },
        {
            "name": "Data Exposure Sensitivity",
            "weight": 0.25,
            "current_value": round(der, 1),
            "explanation": f"Accesses data asset with sensitivity level {max_data_sensitivity}/5."
        },
        {
            "name": "Business Impact Criticality",
            "weight": 0.15,
            "current_value": round(bir, 1),
            "explanation": f"System of record criticality level is {system_criticality}/5."
        },
        {
            "name": "Vendor Trust & Security Posture",
            "weight": 0.15,
            "current_value": round(vsr, 1),
            "explanation": f"Vendor trust score evaluated at {vendor_trust_score}/100."
        },
        {
            "name": "Attack Path Reachability",
            "weight": 0.15,
            "current_value": round(apr, 1),
            "explanation": "Application is part of an active attack path to sensitive assets." if in_attack_path else "No active multi-hop attack path detected."
        }
    ]
    
    return {
        "overall_score": overall_score,
        "severity": severity,
        "risk_engine_version": RISK_ENGINE_VERSION,
        "context_multiplier": round(context_multiplier, 2),
        "dimensions": {
            "technical_risk": round(tr, 1),
            "data_exposure_risk": round(der, 1),
            "business_impact_risk": round(bir, 1),
            "vendor_risk": round(vsr, 1),
            "attack_path_risk": round(apr, 1)
        },
        "factors": factors
    }
