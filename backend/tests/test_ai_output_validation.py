"""
test_ai_output_validation.py
Tests Pydantic schema validation for AI Security Analyst responses.
"""
import pytest
from app.ai.schemas import AIAnalysisResponse, ClaimGrounding, SecurityObjectRef, Recommendation


def test_ai_analysis_response_schema_validation():
    """Verifies AIAnalysisResponse enforces mandatory fields and Pydantic types."""
    res = AIAnalysisResponse(
        answer="### Security Briefing\nEverything is secure.",
        summary="All systems nominal.",
        severity="LOW",
        confidence="HIGH",
        claims=[
            ClaimGrounding(claim="Claim A", evidence_ids=["ev-1"])
        ],
        security_objects=[
            SecurityObjectRef(type="APPLICATION", id="app-1", display_name="Test App")
        ],
        recommendations=[
            Recommendation(action="Action A", source="DETERMINISTIC_RECOMMENDATION")
        ],
        limitations=["Advisory mode."]
    )

    assert res.severity == "LOW"
    assert res.confidence == "HIGH"
    assert len(res.claims) == 1
    assert res.claims[0].evidence_ids == ["ev-1"]
