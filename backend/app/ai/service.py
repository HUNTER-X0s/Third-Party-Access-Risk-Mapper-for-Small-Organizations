"""
app/ai/service.py
Core AI Security Analyst Orchestration Service.
Connects authorization, context building, tool guard, Gemini provider, and citation validation.
"""
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.ai.providers.base import AIProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.context_builder import AIContextBuilder
from app.ai.citation_validator import CitationValidator
from app.ai.system_prompts import SECURITY_ANALYST_SYSTEM_INSTRUCTION
from app.ai.schemas import AIAnalysisResponse, AIAnalysisRequest

logger = logging.getLogger(__name__)


class AISecurityAnalystService:
    """
    High-level AI Security Analyst orchestrator.
    Guarantees that AI analysis is strictly read-only, tenant-isolated, and evidence-grounded.
    """

    def __init__(self, db: Session, organization_id: str, provider: Optional[AIProvider] = None):
        self.db = db
        self.org_id = organization_id
        self.provider = provider or GeminiProvider()
        self.context_builder = AIContextBuilder(db, organization_id)

    async def analyze_query(self, req: AIAnalysisRequest) -> AIAnalysisResponse:
        """
        Orchestrate contextual AI analysis:
          1. Build tenant-isolated authorized context.
          2. Apply prompt boundaries and system security policy.
          3. Invoke AI Provider (Gemini / Offline Fallback).
          4. Validate and sanitize evidence citations.
        """
        # Step 1: Build context based on requested context_type
        if req.context_type == "APPLICATION" and req.entity_id:
            context = self.context_builder.build_application_context(req.entity_id)
        elif req.context_type == "FINDING" and req.entity_id:
            context = self.context_builder.build_finding_context(req.entity_id)
        elif req.context_type == "SNAPSHOT" and req.entity_id and ":" in req.entity_id:
            id_a, id_b = req.entity_id.split(":", 1)
            context = self.context_builder.build_snapshot_diff_context(id_a, id_b)
        else:
            context = self.context_builder.build_general_context()

        # Handle unauthorized or missing object errors
        if "error" in context:
            return AIAnalysisResponse(
                answer=f"⚠️ Security Access Error: {context['error']}",
                summary="Unauthorized or missing security entity context.",
                severity="HIGH",
                confidence="HIGH",
                claims=[],
                security_objects=[],
                recommendations=[],
                limitations=["Access denied to requested entity or entity does not exist in this organization."]
            )

        # Step 2: System prompt instruction
        instruction = SECURITY_ANALYST_SYSTEM_INSTRUCTION
        if req.mode == "EXECUTIVE":
            instruction += "\nMODE: EXECUTIVE BRIEFING. Provide concise, high-level business impact language suitable for leadership."

        # Step 3: Invoke AI Provider
        raw_response = await self.provider.analyze(
            system_instruction=instruction,
            user_question=req.question,
            structured_context=context
        )

        # Step 4: Validate citations against authorized context
        sanitized_response = CitationValidator.sanitize_response_citations(raw_response, context)

        return sanitized_response
