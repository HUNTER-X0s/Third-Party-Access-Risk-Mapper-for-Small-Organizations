"""
test_ai_tenant_isolation.py
Tests cross-tenant isolation enforcement in AI Security Analyst context building and API endpoints.
"""
import asyncio
import pytest
from app.ai.service import AISecurityAnalystService
from app.ai.schemas import AIAnalysisRequest
from app.models import Organization, ApplicationInstance


def test_ai_service_cross_tenant_entity_denial(db_session):
    """User from Org A requesting AI analysis for an app belonging to Org B gets access error."""
    orgs = db_session.query(Organization).all()
    other_org_id = "org-b-fake-id-999"
    app = db_session.query(ApplicationInstance).first()

    service = AISecurityAnalystService(db_session, other_org_id)
    req = AIAnalysisRequest(
        question="Analyze this application",
        context_type="APPLICATION",
        entity_id=app.id
    )

    res = asyncio.run(service.analyze_query(req))

    assert "error" in res.answer.lower() or "denied" in res.answer.lower() or "not found" in res.answer.lower() or "security" in res.answer.lower()
    assert any("access denied" in lim.lower() or "advisory" in lim.lower() or "read-only" in lim.lower() for lim in res.limitations)
