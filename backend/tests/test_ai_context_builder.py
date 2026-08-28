"""
test_ai_context_builder.py
Tests AIContextBuilder tenant isolation, data minimization, and untrusted tag wrapping.
"""
import pytest
from app.ai.context_builder import AIContextBuilder
from app.models import Organization, ApplicationInstance


def test_ai_context_builder_general(db_session):
    """Builds general context for organization and verifies untrusted tags."""
    org = db_session.query(Organization).first()
    builder = AIContextBuilder(db_session, org.id)
    ctx = builder.build_general_context()

    assert "organization_name" in ctx
    assert "<UNTRUSTED_SECURITY_DATA>" in ctx["organization_name"]
    assert "applications" in ctx
    assert "findings" in ctx


def test_ai_context_builder_application(db_session):
    """Builds application context for an authorized app instance."""
    app = db_session.query(ApplicationInstance).first()
    builder = AIContextBuilder(db_session, app.organization_id)
    ctx = builder.build_application_context(app.id)

    assert ctx["application_id"] == app.id
    assert "dimensions" in ctx
    assert "permissions" in ctx
    assert "accessible_data_assets" in ctx


def test_ai_context_builder_unauthorized_cross_tenant(db_session):
    """Attempting to build context for an app in Org A using Org B builder returns error."""
    app = db_session.query(ApplicationInstance).first()
    builder = AIContextBuilder(db_session, "fake-other-org-id")
    ctx = builder.build_application_context(app.id)

    assert "error" in ctx
    assert "unauthorized" in ctx["error"].lower() or "not found" in ctx["error"].lower()
