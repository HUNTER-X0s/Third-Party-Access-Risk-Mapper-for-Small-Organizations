# AccessGuard Phase 6 — AI Governance & Safety Rules

## 1. Principles of Secure AI Governance

AccessGuard enforces strict AI governance boundaries to prevent AI hallucination, prompt injection, data leakage, and unauthorized agency.

---

## 2. Mandatory AI Safety Rules

| Boundary Domain | Safety Rule | Implementation Mechanism |
|---|---|---|
| **Authoritative Engine** | AI MUST NOT calculate risk scores or override deterministic finding severities. | `SystemPrompt` + `CitationValidator` |
| **Tenant Isolation** | AI context is generated strictly from server-derived `organization_id`. Frontend input cannot override tenant filters. | `AIContextBuilder` tenant filter |
| **RBAC Authorization** | AI endpoints enforce backend role checks (`require_role`). Users inspect only authorized security objects. | `api/v1/endpoints/ai.py` |
| **Read-Only Guard** | Tool registry permits only `READ_ONLY` capabilities. `WRITE` and `EXECUTE` raise `SecurityViolationError`. | `AIToolRegistry` |
| **Data Minimization** | Secrets, JWTs, private keys, passwords, and raw PII are redacted prior to AI context building. | `_SECRET_PATTERN.sub("[REDACTED]")` |
| **Prompt Injection** | External data (app names, descriptions, scopes) is wrapped in `<UNTRUSTED_SECURITY_DATA>` delimiters. | `_sanitize_untrusted_text()` |
| **Evidence Grounding** | Claims cite explicit evidence IDs (`EV-XXX`). Hallucinated or unauthorized citations are stripped. | `CitationValidator.sanitize_response_citations()` |
| **Action Authority** | Clear UI distinction between `DETERMINISTIC_RECOMMENDATION` and `AI_SUGGESTION`. AI buttons never execute mutations. | `AIAnalystDrawer.tsx` |

---

## 3. Rate Limiting & Resource Protection

- **Daily Request Quota**: Tracked per organization (`AI_DAILY_RATE_LIMIT = 100`).
- **Request Timeout**: Strict 15-second timeout (`AI_REQUEST_TIMEOUT_SECONDS = 15`).
- **Graceful Fallback**: Returns deterministic security fallback if daily limit or timeout is reached.
