"""
app/ai/citation_validator.py
Grounding and citation validator for the AI Security Analyst.
Ensures that evidence IDs and security object IDs in AI responses are authentic
and were explicitly present in the authorized tenant context.
"""
import logging
from typing import Dict, Any, Set
from app.ai.schemas import AIAnalysisResponse, ClaimGrounding, SecurityObjectRef

logger = logging.getLogger(__name__)


class CitationValidator:
    """
    Validates model output citations against authorized context IDs.
    Strips or flags hallucinated / unauthorized object citations.
    """

    @staticmethod
    def extract_valid_ids(authorized_context: Dict[str, Any]) -> Set[str]:
        """Extract all valid UUIDs / entity IDs from the authorized context payload."""
        valid_ids: Set[str] = set()

        def _traverse(node):
            if isinstance(node, dict):
                for k, v in node.items():
                    if k in ("id", "application_id", "finding_id", "data_asset_id", "vendor_id", "snapshot_a_id", "snapshot_b_id") and isinstance(v, str):
                        valid_ids.add(v)
                    _traverse(v)
            elif isinstance(node, list):
                for item in node:
                    _traverse(item)

        _traverse(authorized_context)
        return valid_ids

    @classmethod
    def sanitize_response_citations(
        cls, response: AIAnalysisResponse, authorized_context: Dict[str, Any]
    ) -> AIAnalysisResponse:
        """
        Filter claims and security objects in response:
        - Removes evidence IDs not present in valid_ids.
        - Removes security object references with invalid IDs.
        - Appends a limitation warning if invalid citations were detected.
        """
        valid_ids = cls.extract_valid_ids(authorized_context)
        has_invalid_citations = False

        # Validate claim evidence IDs
        sanitized_claims = []
        for c in response.claims:
            filtered_eids = [eid for eid in c.evidence_ids if eid in valid_ids]
            if len(filtered_eids) != len(c.evidence_ids):
                has_invalid_citations = True
                logger.warning("Stripped hallucinated/unauthorized evidence citation(s) from AI claim.")
            sanitized_claims.append(ClaimGrounding(
                claim=c.claim,
                evidence_ids=filtered_eids
            ))

        # Validate security object references
        sanitized_objects = []
        for obj in response.security_objects:
            if obj.id in valid_ids:
                sanitized_objects.append(obj)
            else:
                has_invalid_citations = True
                logger.warning("Stripped hallucinated/unauthorized security object reference: %s", obj.id)

        response.claims = sanitized_claims
        response.security_objects = sanitized_objects

        if has_invalid_citations:
            response.limitations.append("One or more ungrounded citations were detected and removed by AccessGuard Security Validator.")

        return response
