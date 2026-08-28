# AccessGuard Phase 6 — AI Security Analyst Architecture

## 1. Executive Summary
The AccessGuard AI Security Analyst provides an evidence-grounded, read-only security copilot over AccessGuard's deterministic security intelligence. The AI layer translates complex third-party access risks, graph attack paths, blast-radius metrics, and snapshot comparisons into human-readable SecOps briefings without ever altering authoritative risk scores or authorization boundaries.

---

## 2. Security System Architecture Flow

```
FRONTEND (AIAnalystDrawer)
  │ HTTPS / JWT Cookie
  ▼
AI ANALYST API Gateway (/api/v1/ai/analyze)
  │ Server-Validated RBAC & Organization Derivation
  ▼
TENANT ISOLATION BOUNDARY (Organization ID Filter)
  │
  ▼
AI CONTEXT BUILDER (Data Minimization & Redaction)
  │ Wraps untrusted text in <UNTRUSTED_SECURITY_DATA>
  ▼
READ-ONLY AI TOOL GUARD (AIToolRegistry)
  │ Blocks WRITE / EXECUTE capabilities
  ▼
GEMINI PROVIDER ABSTRACTION (GeminiProvider — gemini-3.6-flash)
  │ Enforces structured JSON output schema
  ▼
STRUCTURED OUTPUT & CITATION VALIDATOR (CitationValidator)
  │ Strips ungrounded evidence/object citations
  ▼
SAFE ADVISORY RESPONSE (AIAnalysisResponse)
```

---

## 3. Core Architectural Rules & Boundaries

1. **Deterministic State is Authoritative**:
   - Risk Engine (`v1.5.0`), Graph Engine, Snapshot Engine, and Remediation Optimizer remain frozen and authoritative.
   - The AI Analyst explains deterministic numbers (e.g. Risk Score = 94.5); it NEVER recalculates or overrides them.

2. **Read-Only Advisory Sandbox**:
   - All write and mutation operations (`revoke_permission`, `execute_remediation`, `change_role`) are strictly forbidden in the AI layer.
   - AIToolRegistry permits ONLY `READ_ONLY` query helpers.

3. **Backend-Managed Credentials**:
   - `settings.GEMINI_API_KEY` is loaded from environment variables on the backend.
   - API keys and tokens are NEVER exposed to the frontend or included in diagnostic logs.

4. **Offline Fallback Guarantee**:
   - If Gemini API key is absent or network fails, `GeminiProvider` generates a deterministic offline security analysis directly from authorized context, ensuring AccessGuard remains 100% operational offline.
