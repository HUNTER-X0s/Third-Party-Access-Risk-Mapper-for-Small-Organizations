"""
test_ai_failure_handling.py
Tests graceful fallback and system resilience when Gemini API fails or times out.
"""
import asyncio
import pytest
from unittest.mock import patch
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.service import AISecurityAnalystService
from app.ai.schemas import AIAnalysisRequest
from app.models import Organization


def test_ai_service_graceful_fallback_on_provider_exception(db_session):
    """When Gemini provider raises an exception, service returns offline fallback without crashing platform."""
    org = db_session.query(Organization).first()
    failing_provider = GeminiProvider(api_key="valid-looking-key")

    service = AISecurityAnalystService(db_session, org.id, provider=failing_provider)
    req = AIAnalysisRequest(question="Analyze risk posture", context_type="GENERAL")

    res = asyncio.run(service.analyze_query(req))

    assert res.answer is not None
    assert res.summary is not None
    assert res.severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")
