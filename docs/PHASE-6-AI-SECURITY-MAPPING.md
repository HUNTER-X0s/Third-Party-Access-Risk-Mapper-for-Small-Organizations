# AccessGuard Phase 6 — OWASP Top 10 for LLM Applications Mapping

## Executive Evaluation Matrix

This document maps AccessGuard's AI Security Analyst implementation against the OWASP Top 10 for LLM Applications (2025/2026 guidelines).

| OWASP Vulnerability | Risk Summary | AccessGuard Countermeasure / Security Control | Status |
|---|---|---|---|
| **LLM01: Prompt Injection** | Untrusted inputs manipulate model instructions or leak secrets. | External text wrapped in `<UNTRUSTED_SECURITY_DATA>` delimiters. System prompt instructs model to treat delimiter contents as data. | ✅ DEFENDED (`test_ai_prompt_injection.py`) |
| **LLM02: Sensitive Information Disclosure** | Model reveals API keys, secrets, or raw PII in output. | `AIContextBuilder` redacts passwords, tokens, and PEM keys with `[REDACTED]` before context building. | ✅ DEFENDED (`test_ai_redaction.py`) |
| **LLM05: Improper Output Handling** | Unsanitized model output executed by downstream client/system. | Pydantic schema validation (`AIAnalysisResponse`). Output rendered as plain text/Markdown; HTML execution disabled. | ✅ DEFENDED (`test_ai_output_validation.py`) |
| **LLM06: Excessive Agency** | LLM executes privileged actions (mutations, role changes, remediation). | `AIToolRegistry` enforces `READ_ONLY` capabilities. Write methods raise `SecurityViolationError`. | ✅ DEFENDED (`test_ai_tool_guard.py`) |
| **LLM07: System Prompt Leakage** | Adversary extracts proprietary system instructions or system prompt. | System prompt boundary rules instruct model to refuse prompt extraction. No keys stored in prompt text. | ✅ DEFENDED (`test_ai_prompt_injection.py`) |
| **LLM09: Misinformation / Hallucination** | Model invents nonexistent evidence IDs, risk scores, or findings. | Deterministic engines calculate scores. `CitationValidator` strips hallucinated evidence/object citations. | ✅ DEFENDED (`test_ai_evidence_grounding.py`) |
| **LLM10: Unbounded Consumption** | Excessive input/output tokens cause denial of service or cost explosion. | Input request length capped at 1,000 characters; request timeout set to 15s; daily rate limit enforced. | ✅ DEFENDED (`config.py`) |

---

*Note: AccessGuard references industry frameworks as design inspiration and alignment mapping. AccessGuard makes no claims of formal third-party certification.*
