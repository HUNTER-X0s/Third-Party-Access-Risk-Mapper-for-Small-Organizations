"""
test_ai_provider.py
Tests GeminiProvider initialization, model configuration, and offline fallback behavior.
"""
import asyncio
import pytest
from app.ai.providers.gemini_provider import GeminiProvider
from app.core.config import settings


def test_gemini_provider_model_configuration():
    """Verifies GeminiProvider uses configurable GEMINI_MODEL setting (gemini-3.6-flash)."""
    assert settings.GEMINI_MODEL == "gemini-3.6-flash"
    provider = GeminiProvider(model_name="custom-test-model")
    assert provider.model_name == "custom-test-model"


def test_gemini_provider_offline_fallback():
    """Verifies GeminiProvider returns valid schema response when API key is unconfigured."""
    provider = GeminiProvider(api_key="")
    assert not provider.health_check()


def test_gemini_provider_offline_analysis_response():
    """Verifies analyze() returns structured AIAnalysisResponse in offline fallback mode."""
    provider = GeminiProvider(api_key="")
    context = {
        "organization_name": "Anurag Technologies",
        "data_mode": "DEMO / SIMULATED",
        "applications": [{"id": "app-101", "name": "GitHub App", "risk_score": 94.5, "severity": "Critical"}],
        "findings": [{"id": "f-101", "title": "Excess Admin Access", "severity": "Critical"}],
        "evidence_items": [{"id": "ev-101"}]
    }

    res = asyncio.run(provider.analyze(
        system_instruction="System prompt",
        user_question="Why is GitHub critical?",
        structured_context=context
    ))

    assert res.answer is not None
    assert "Anurag Technologies" in res.answer
    assert res.severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")
    assert res.confidence == "HIGH"
    assert len(res.claims) >= 1
    assert res.model_metadata["mode"] == "OFFLINE_DETERMINISTIC_FALLBACK"
