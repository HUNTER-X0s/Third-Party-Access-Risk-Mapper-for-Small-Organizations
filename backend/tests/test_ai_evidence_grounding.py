"""
test_ai_evidence_grounding.py
Tests CitationValidator hallucination stripping and evidence grounding.
"""
import pytest
from app.ai.citation_validator import CitationValidator
from app.ai.schemas import AIAnalysisResponse, ClaimGrounding, SecurityObjectRef


def test_citation_validator_strips_hallucinated_evidence_ids():
    """CitationValidator must strip evidence IDs not present in authorized context."""
    authorized_context = {
        "applications": [{"id": "app-101"}],
        "evidence_items": [{"id": "ev-authentic-1"}]
    }

    response = AIAnalysisResponse(
        answer="Analysis text.",
        summary="Summary text.",
        severity="MEDIUM",
        confidence="HIGH",
        claims=[
            ClaimGrounding(claim="Valid claim", evidence_ids=["ev-authentic-1", "ev-hallucinated-999"])
        ],
        security_objects=[
            SecurityObjectRef(type="APPLICATION", id="app-101"),
            SecurityObjectRef(type="APPLICATION", id="app-hallucinated-888")
        ],
        recommendations=[],
        limitations=[]
    )

    sanitized = CitationValidator.sanitize_response_citations(response, authorized_context)

    # Hallucinated evidence ID must be stripped
    assert sanitized.claims[0].evidence_ids == ["ev-authentic-1"]
    # Hallucinated security object must be stripped
    assert len(sanitized.security_objects) == 1
    assert sanitized.security_objects[0].id == "app-101"
    # Limitation warning appended
    assert any("ungrounded" in lim.lower() for lim in sanitized.limitations)
