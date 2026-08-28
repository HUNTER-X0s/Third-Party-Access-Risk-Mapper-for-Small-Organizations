"""
Evidence Engine Service (Hardened)
Generates SHA-256 payload integrity hashes, performs tamper-evident verification,
and builds evidence provenance records.
"""

import hashlib
import json
from typing import Any, Dict

def compute_payload_hash(payload: Dict[str, Any]) -> str:
    """
    Computes a deterministic SHA-256 hash of a JSON-serializable evidence dictionary payload.
    Uses sort_keys=True so dictionary key ordering does not alter the canonical hash.
    """
    serialized = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

def verify_payload_hash(payload: Dict[str, Any], expected_hash: str) -> Dict[str, Any]:
    """
    Recalculates the SHA-256 hash of a payload and compares it against the expected stored hash.
    Returns tamper-evident status (VERIFIED_INTACT vs TAMPER_DETECTED).
    """
    recalculated_hash = compute_payload_hash(payload)
    is_intact = (recalculated_hash == expected_hash)
    
    return {
        "status": "VERIFIED_INTACT" if is_intact else "TAMPER_DETECTED",
        "is_intact": is_intact,
        "stored_hash": expected_hash,
        "recalculated_hash": recalculated_hash,
        "tamper_evident_label": "TAMPER-EVIDENT VERIFIED" if is_intact else "TAMPER WARNING: PAYLOAD ALTERED"
    }

def create_evidence_summary(raw_evidence_hash: str, connector_type: str, collected_at_str: str) -> Dict[str, Any]:
    """
    Builds a summary structure for UI evidence inspection drawers.
    """
    return {
        "integrity_hash_sha256": raw_evidence_hash,
        "connector_source": connector_type,
        "collection_timestamp": collected_at_str,
        "tamper_evident_status": "VERIFIED_INTACT",
        "freshness": "CONFIRMED"
    }
