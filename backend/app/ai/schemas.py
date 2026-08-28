"""
app/ai/schemas.py
Pydantic schemas for the AI Security Analyst structured output and API endpoints.
Enforces strict schema validation — AccessGuard NEVER parses unconstrained prose.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class ClaimGrounding(BaseModel):
    """Factual security claim with traceable evidence citations."""
    claim: str = Field(..., description="Factual security claim grounded in evidence.")
    evidence_ids: List[str] = Field(default_factory=list, description="IDs of RawEvidence or SecurityFacts supporting this claim.")


class SecurityObjectRef(BaseModel):
    """Reference to an authorized AccessGuard domain object."""
    type: str = Field(..., description="APPLICATION, FINDING, DATA_ASSET, VENDOR, PATH, or SNAPSHOT")
    id: str = Field(..., description="Primary key UUID of the referenced security object.")
    display_name: Optional[str] = Field(None, description="Human-readable name of the object.")


class Recommendation(BaseModel):
    """Action recommendation labeled clearly by authoritative source."""
    action: str = Field(..., description="Recommended risk mitigation step.")
    source: str = Field(..., description="DETERMINISTIC_RECOMMENDATION or AI_SUGGESTION")


class AIAnalysisResponse(BaseModel):
    """
    Mandatory structured output schema for the AI Security Analyst.
    All AI responses MUST adhere strictly to this schema.
    """
    answer: str = Field(..., description="Primary security analyst response in clean GitHub Markdown.")
    summary: str = Field(..., description="1-2 sentence executive summary.")
    severity: str = Field(..., description="Severity level: LOW, MEDIUM, HIGH, CRITICAL, or INFO.")
    confidence: str = Field(..., description="Confidence level: HIGH, MEDIUM, or LOW.")
    claims: List[ClaimGrounding] = Field(default_factory=list, description="Evidence-backed claims.")
    security_objects: List[SecurityObjectRef] = Field(default_factory=list, description="Referenced security objects.")
    recommendations: List[Recommendation] = Field(default_factory=list, description="Prioritized recommendations.")
    limitations: List[str] = Field(default_factory=list, description="Explicit security boundary limitations or data staleness warnings.")
    model_metadata: Optional[dict] = Field(default_factory=dict, description="Model ID, prompt version, latency, grounding count.")


class AIAnalysisRequest(BaseModel):
    """API request schema for contextual AI security analysis."""
    question: str = Field(..., max_length=1000, description="Security question or investigation prompt.")
    context_type: str = Field("GENERAL", description="GENERAL, APPLICATION, FINDING, DATA_ASSET, VENDOR, PATH, SNAPSHOT, EXECUTIVE")
    entity_id: Optional[str] = Field(None, description="Target entity UUID for contextual analysis.")
    mode: str = Field("TECHNICAL", description="TECHNICAL or EXECUTIVE")
