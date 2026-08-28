"""
test_ai_redaction.py
Tests secret redaction in AIContextBuilder before context is injected into AI prompts.
"""
import pytest
from app.ai.context_builder import AIContextBuilder


def test_ai_context_builder_secret_redaction(db_session):
    """AIContextBuilder redacts passwords, tokens, and private keys from untrusted text fields."""
    builder = AIContextBuilder(db_session, "fake-org")

    text_with_secret = "GitHub App authorization token ghp_secret_access_token and private_key PEM"
    sanitized = builder._sanitize_untrusted_text(text_with_secret)

    # Secrets must be replaced with [REDACTED]
    assert "[REDACTED]" in sanitized
    assert "ghp_secret_access_token" not in sanitized
    assert "<UNTRUSTED_SECURITY_DATA>" in sanitized
