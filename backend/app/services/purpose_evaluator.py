"""
Business Purpose & Excess Access Evaluator
Determines excess permissions and purpose/data mismatches using set difference logic.
"""

from typing import List, Dict, Set, Any

def evaluate_excess_permissions(
    granted_scopes: List[str],
    required_canonical_permissions: List[str],
    optional_canonical_permissions: List[str] = None
) -> Dict[str, Any]:
    """
    Computes excess permissions by comparing granted raw scopes normalized against allowed permissions.
    Returns excess_scopes, excess_ratio, is_excess_detected.
    """
    optional_canonical_permissions = optional_canonical_permissions or []
    allowed_canonical = set(required_canonical_permissions) | set(optional_canonical_permissions)
    
    excess_scopes = []
    for scope in granted_scopes:
        from app.services.scope_normalizer import normalize_scope
        canonical, _, _, _ = normalize_scope(scope)
        if canonical not in allowed_canonical:
            excess_scopes.append(scope)
            
    total_granted = len(granted_scopes)
    excess_count = len(excess_scopes)
    excess_ratio = (excess_count / total_granted) if total_granted > 0 else 0.0
    
    return {
        "excess_scopes": excess_scopes,
        "excess_count": excess_count,
        "total_granted": total_granted,
        "excess_ratio": excess_ratio,
        "is_excess_detected": excess_count > 0
    }

def evaluate_purpose_data_mismatch(
    expected_data_categories: List[str],
    actual_reachable_data_categories: List[str]
) -> Dict[str, Any]:
    """
    Evaluates whether an application accesses significantly broader data categories than expected by its purpose.
    """
    expected_set = set(expected_data_categories)
    actual_set = set(actual_reachable_data_categories)
    
    unexpected_data = list(actual_set - expected_set)
    is_mismatch = len(unexpected_data) > 0
    
    return {
        "is_mismatch": is_mismatch,
        "unexpected_data_categories": unexpected_data,
        "expected_categories": expected_data_categories,
        "actual_categories": actual_reachable_data_categories
    }
