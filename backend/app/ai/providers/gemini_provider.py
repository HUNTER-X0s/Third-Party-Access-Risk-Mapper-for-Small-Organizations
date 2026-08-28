"""
app/ai/providers/gemini_provider.py
Google Gemini AI Provider implementation (gemini-3.6-flash).
Uses structured outputs, timeout bounds, and graceful offline fallback.
"""
import time
import json
import logging
from typing import Dict, Any, Optional
import httpx

from app.ai.providers.base import AIProvider
from app.ai.schemas import (
    AIAnalysisResponse, ClaimGrounding, SecurityObjectRef, Recommendation
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider):
    """
    Google Gemini Provider for AccessGuard.
    Supports Gemini 3.6 Flash (`gemini-3.6-flash`) with structured JSON output enforcement.
    API keys are managed strictly via environment (`settings.GEMINI_API_KEY`).
    """

    PROVIDER_NAME = "GOOGLE_GEMINI"

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL or "gemini-3.6-flash"

    def health_check(self) -> bool:
        """Check if Gemini API key is configured."""
        return bool(self.api_key and len(self.api_key) > 5)

    async def analyze(
        self,
        system_instruction: str,
        user_question: str,
        structured_context: Dict[str, Any],
        model_name: Optional[str] = None
    ) -> AIAnalysisResponse:
        """
        Execute security analysis via Gemini API or return a deterministic fallback response
        if credentials are absent or network is offline.
        """
        target_model = model_name or self.model_name
        start_time = time.time()

        if not self.health_check():
            logger.info("Gemini API key not configured — returning offline security analysis fallback.")
            return self._build_offline_fallback(user_question, structured_context, target_model, start_time)

        try:
            # Build API URL (Google AI Studio REST endpoint)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={self.api_key}"

            # Format payload with system instruction, structured context, and response schema
            prompt_text = (
                f"{system_instruction}\n\n"
                f"<SECURITY_CONTEXT>\n{json.dumps(structured_context, indent=2, default=str)}\n</SECURITY_CONTEXT>\n\n"
                f"<USER_QUESTION>\n{user_question}\n</USER_QUESTION>\n\n"
                f"Respond exclusively in valid JSON adhering to the AIAnalysisResponse schema."
            )

            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt_text}
                        ]
                    }
                ],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "temperature": 0.2,
                    "maxOutputTokens": 2048,
                }
            }

            async with httpx.AsyncClient(timeout=httpx.Timeout(settings.AI_REQUEST_TIMEOUT_SECONDS)) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        parsed_json = json.loads(text_content)
                        parsed_json["model_metadata"] = {
                            "provider": self.PROVIDER_NAME,
                            "model": target_model,
                            "latency_ms": int((time.time() - start_time) * 1000),
                            "mode": "LIVE_GEMINI",
                        }
                        return AIAnalysisResponse(**parsed_json)

            logger.warning("Gemini API call failed status=%s — falling back to offline analysis.", response.status_code)
            return self._build_offline_fallback(user_question, structured_context, target_model, start_time)

        except Exception as e:
            logger.warning("Gemini provider exception (%s) — returning offline security analysis fallback.", e)
            return self._build_offline_fallback(user_question, structured_context, target_model, start_time)

    def _build_offline_fallback(
        self, question: str, context: Dict[str, Any], model: str, start_time: float
    ) -> AIAnalysisResponse:
        """
        Deterministic, offline security analysis fallback.
        Parses authorized context directly to construct an evidence-grounded response.
        Ensures AccessGuard remains 100% operational offline.
        """
        org_name = context.get("organization_name", "Anurag Technologies")
        apps = context.get("applications", [])
        findings = context.get("findings", [])
        evidence_list = context.get("evidence_items", [])
        data_mode = context.get("data_mode", "DEMO / SIMULATED")

        # Factual claims & citations
        claims = []
        objects = []
        recs = []

        if apps:
            top_app = apps[0]
            objects.append(SecurityObjectRef(
                type="APPLICATION",
                id=top_app.get("id", "app-1"),
                display_name=top_app.get("name", "Third-Party App")
            ))
            claims.append(ClaimGrounding(
                claim=f"Application '{top_app.get('name')}' carries a deterministic risk score of {top_app.get('risk_score', 'N/A')} ({top_app.get('severity', 'Medium')}).",
                evidence_ids=[e.get("id") for e in evidence_list[:2] if e.get("id")]
            ))

        if findings:
            top_finding = findings[0]
            objects.append(SecurityObjectRef(
                type="FINDING",
                id=top_finding.get("id", "finding-1"),
                display_name=top_finding.get("title", "Risk Finding")
            ))
            recs.append(Recommendation(
                action=f"Remediate finding: {top_finding.get('title')}",
                source="DETERMINISTIC_RECOMMENDATION"
            ))

        recs.append(Recommendation(
            action="Run provider synchronization to verify current scope state.",
            source="AI_SUGGESTION"
        ))

        latency = int((time.time() - start_time) * 1000)

        answer_markdown = (
            f"### Security Analysis — {org_name}\n\n"
            f"**Query:** {question}\n\n"
            f"**Data Context Mode:** `{data_mode}`\n\n"
            f"#### Factual Overview\n"
            f"Based on current AccessGuard deterministic security state, the organization currently monitors "
            f"**{len(apps)} third-party application(s)** and **{len(findings)} active finding(s)**.\n\n"
            f"#### Key Findings & Evidence Grounding\n"
        )
        for c in claims:
            answer_markdown += f"- **Claim:** {c.claim}\n"
            if c.evidence_ids:
                answer_markdown += f"  - *Evidence Citations:* {', '.join(c.evidence_ids)}\n"

        answer_markdown += (
            f"\n#### Architectural Note\n"
            f"All risk scores, attack paths, and blast radius metrics are derived deterministically from AccessGuard's core engines (`risk_engine_v1.5.0`). "
            f"The AI Analyst operates strictly in read-only advisory mode."
        )

        return AIAnalysisResponse(
            answer=answer_markdown,
            summary=f"SecOps security analysis for {org_name} ({len(apps)} app(s), {len(findings)} finding(s)).",
            severity="HIGH" if any(f.get("severity") in ("Critical", "High") for f in findings) else "MEDIUM",
            confidence="HIGH",
            claims=claims,
            security_objects=objects,
            recommendations=recs,
            limitations=[
                "AI Analyst operating in read-only advisory mode.",
                f"Data source status: {data_mode}.",
                "Deterministic engine values are authoritative."
            ],
            model_metadata={
                "provider": self.PROVIDER_NAME,
                "model": model,
                "latency_ms": latency,
                "mode": "OFFLINE_DETERMINISTIC_FALLBACK"
            }
        )
