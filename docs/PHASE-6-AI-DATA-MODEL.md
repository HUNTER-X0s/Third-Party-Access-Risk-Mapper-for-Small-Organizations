# AccessGuard Phase 6 — AI Structured Output & Data Model

## 1. Structured Output Schema Design

AccessGuard NEVER parses unconstrained prose for security analyst operations. All responses are validated against the `AIAnalysisResponse` Pydantic schema.

```json
{
  "answer": "### Security Briefing\nGitHub App carries a high risk score...",
  "summary": "High risk detected on GitHub App integration.",
  "severity": "HIGH",
  "confidence": "HIGH",
  "claims": [
    {
      "claim": "GitHub App holds organization-level administrative access.",
      "evidence_ids": ["ev-102", "ev-103"]
    }
  ],
  "security_objects": [
    {
      "type": "APPLICATION",
      "id": "761b4e57-955c-40e6-886b-fd7112d88698",
      "display_name": "GitHub App"
    }
  ],
  "recommendations": [
    {
      "action": "Revoke organization_admin permission scope.",
      "source": "DETERMINISTIC_RECOMMENDATION"
    },
    {
      "action": "Re-run provider sync after permission reduction.",
      "source": "AI_SUGGESTION"
    }
  ],
  "limitations": [
    "AI Analyst operating in read-only advisory mode.",
    "Deterministic engine values are authoritative."
  ],
  "model_metadata": {
    "provider": "GOOGLE_GEMINI",
    "model": "gemini-3.6-flash",
    "mode": "LIVE_GEMINI",
    "latency_ms": 340
  }
}
```

---

## 2. Telemetry & Audit Log Schema

AI queries record audit events in the append-only `AuditEvent` table:

```json
{
  "organization_id": "bed69ec2-4d89-4894-aebb-e8c533ae3704",
  "actor_email": "admin@anurag.tech",
  "action": "AI_QUERY_PERFORMED",
  "target_type": "AISecurityAnalyst",
  "target_id": "APPLICATION",
  "outcome": "SUCCESS",
  "event_metadata": {
    "question": "Why is GitHub critical?",
    "context_type": "APPLICATION",
    "entity_id": "761b4e57-955c-40e6-886b-fd7112d88698",
    "mode": "TECHNICAL",
    "model": "gemini-3.6-flash"
  }
}
```
*Note: Prompts containing secrets, JWTs, or raw credentials are NEVER logged.*
