# AccessGuard: Final Product Limitations & Boundary Register

**Date:** 2026-08-14  
**Policy:** Strict Engineering Honesty (No Unsupported Marketing Claims)

---

## 1. Explicit Architectural Limitations

| Capability Area | Current Implementation | Explicit Boundary & Gaps |
|---|---|---|
| **Live GitHub Integration** | Live read-only GitHub App connector with secret redaction and permission normalization. | Live write/revocation is deliberately prohibited (`READ=True, WRITE=False`). Only GitHub is integrated live; other providers use synthetic seed mappings. |
| **Live Gemini AI Integration** | Fully integrated Gemini 2.5 Flash with prompt sanitization, citation verification, and structured output. | AI is strictly advisory. It cannot alter risk scores, change findings, modify due diligence assessments, or execute remediations. |
| **Database Architecture** | SQLite for demo mode, PostgreSQL ORM models with row-level tenant filtering. | Multi-node distributed clustering and multi-region database replication are not implemented in the hackathon build. |
| **C-SCRM & NIST Due Diligence** | Four-domain scoring (FOCI, Provenance, Resilience, Foundational Cyber Practices) aligned with NIST SP 1326. | Selected indicators evaluated (MFA, Vuln Mgmt, Incident Response, Backup Testing). Full government certification or exhaustive supply-chain audits are not claimed. |
| **Remediation Execution** | Graph-state verified remediation simulator and minimum effective scope optimizer. | Automated direct SaaS API revocation is not executed (deliberate safety constraint; outputs actionable admin runbooks instead). |
| **External Notifications** | In-app notification center with read/unread tracking and fingerprint deduplication. | External email/Slack webhooks require operator SMTP/webhook endpoint configuration in environment variables. |

---

## 2. Safe Operational Language

- AccessGuard is **"ALIGNED WITH NIST SP 1326 / NIST SP 800-161"**, not certified.
- All non-connected demo integrations are labeled **"SYNTHETIC DEMO DATA"**.
- Single-supplier failure impact calculations are labeled **"SIMULATION ONLY — POTENTIAL BUSINESS IMPACT"**.
