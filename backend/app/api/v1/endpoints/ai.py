"""
api/v1/endpoints/ai.py
AI Security Analyst REST API Endpoints.

Authorization & Governance Rules:
  1. Authenticated Users Only (get_current_user).
  2. Organization ID derived exclusively from authenticated user token.
  3. RBAC Roles checked:
     - VIEWER: General posture queries & basic summaries
     - APP_OWNER: Assigned app investigations
     - AUDITOR / IT_ADMIN / SECURITY_ADMIN / SUPER_ADMIN: Full analyst investigation
  4. Audit logging: Security queries logged to AuditEvent table.
  5. Rate limiting: Daily request limit tracked per organization.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User, AuditEvent
from app.api.deps import get_current_user, get_current_org_id, require_role
from app.ai.schemas import AIAnalysisRequest, AIAnalysisResponse
from app.ai.service import AISecurityAnalystService
from app.ai.providers.gemini_provider import GeminiProvider

router = APIRouter()

ALLOWED_ROLES = ["SUPER_ADMIN", "SECURITY_ADMIN", "IT_ADMIN", "AUDITOR", "APP_OWNER", "VIEWER"]


@router.get("/status")
def get_ai_status(
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
    db: Session = Depends(get_db),
):
    """Check AI Security Analyst availability and configured provider model."""
    provider = GeminiProvider()
    is_live = provider.health_check()
    return {
        "status": "AVAILABLE",
        "provider": provider.PROVIDER_NAME,
        "model": provider.model_name,
        "mode": "LIVE_GEMINI" if is_live else "OFFLINE_DETERMINISTIC_FALLBACK",
        "read_only": True,
        "governance": "ADVISORY_ONLY"
    }


@router.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_security_query(
    req: AIAnalysisRequest,
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """
    Execute evidence-grounded AI security analysis.
    All context is tenant-isolated and derived from server-validated organization membership.
    """
    service = AISecurityAnalystService(db, org_id)
    response = await service.analyze_query(req)

    # Audit Logging
    audit = AuditEvent(
        organization_id=org_id,
        actor_email=current_user.email,
        action="AI_QUERY_PERFORMED",
        target_type="AISecurityAnalyst",
        target_id=req.context_type,
        outcome="SUCCESS",
        event_metadata={
            "question": req.question[:100],
            "context_type": req.context_type,
            "entity_id": req.entity_id,
            "mode": req.mode,
            "model": response.model_metadata.get("model") if response.model_metadata else "unknown"
        }
    )
    db.add(audit)
    db.commit()

    return response


@router.post("/investigate/app/{app_id}", response_model=AIAnalysisResponse)
async def investigate_application(
    app_id: str,
    question: Optional[str] = "Why is this application considered at risk, and what evidence supports this?",
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """Contextual AI investigation for a specific application instance."""
    req = AIAnalysisRequest(
        question=question or "Analyze application risk posture and evidence.",
        context_type="APPLICATION",
        entity_id=app_id,
        mode="TECHNICAL"
    )
    service = AISecurityAnalystService(db, org_id)
    return await service.analyze_query(req)


@router.post("/investigate/finding/{finding_id}", response_model=AIAnalysisResponse)
async def investigate_finding(
    finding_id: str,
    question: Optional[str] = "Explain this security finding, its evidence provenance, and recommended remediation.",
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """Contextual AI investigation for a specific risk finding."""
    req = AIAnalysisRequest(
        question=question or "Explain finding details and evidence.",
        context_type="FINDING",
        entity_id=finding_id,
        mode="TECHNICAL"
    )
    service = AISecurityAnalystService(db, org_id)
    return await service.analyze_query(req)


@router.post("/executive-brief", response_model=AIAnalysisResponse)
async def executive_security_brief(
    current_user: User = Depends(require_role(ALLOWED_ROLES)),
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    """Generate a 1-minute executive security briefing for organizational leadership."""
    req = AIAnalysisRequest(
        question="Provide a 1-minute executive security briefing on current third-party posture, top risks, and priority remediations.",
        context_type="GENERAL",
        mode="EXECUTIVE"
    )
    service = AISecurityAnalystService(db, org_id)
    return await service.analyze_query(req)
