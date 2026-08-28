# DECISION-LOG.md
# AccessGuard: Architectural Decision Log

**Document Type:** Decision Log — All Phases  
**Maintained by:** Principal Architect  
**Last Updated:** 2026-08-13  

---

## ADR-001: Modular Monolith Over Microservices
*See Phase 0 specification.*

## ADR-002: Risk Scoring is Deterministic; AI May Not Influence Scores
*See Phase 0 specification.*

## ADR-003: PostgreSQL as Primary Database, SQLite for Demo
*See Phase 0 specification.*

## ADR-004: React + TypeScript for Frontend
*See Phase 0 specification.*

## ADR-005: FastAPI + Python for Backend
*See Phase 0 specification.*

## ADR-006: External Data Treated as Untrusted
*See Phase 0 specification.*

## ADR-007: Tailwind CSS + shadcn/ui for Styling
*See Phase 0 specification.*

## ADR-008: JWT (RS256) + HttpOnly Cookies for Authentication
*See Phase 0 specification.*

## ADR-009: Demo Must Work Offline with Seeded Data
*See Phase 0 specification.*

## ADR-010: AI Layer is Isolated and Advisory Only
*See Phase 0 specification.*

---

## ADR-011: Strict Operational Product Design Language (AG-DS)
**Decision**: AccessGuard frontend will adhere strictly to a high-density, dark slate, operational SecOps design system (AG-DS). Generic AI dashboard conventions (purple gradients, glowing borders, card nesting, decorative floating blobs) are permanently prohibited.  
**Date**: 2026-08-13  
**Reason**: To ensure the platform looks like an enterprise-grade security tool designed by professional security engineers, preventing it from appearing like an AI-generated hackathon template.  
**Consequences**: Custom UI tokens, compact tables, monospaced data fields, split-pane drawers mandatory across all UI views.

---

## ADR-012: Immutable Evidence & Provenance Chain
**Decision**: Every risk finding and permission grant MUST link to an immutable `Evidence` record containing raw provider API payloads, collection timestamps, SHA-256 payload hashes, and normalization rule versions.  
**Date**: 2026-08-13  
**Reason**: Auditors and CISOs require verifiable proof. Scores without traceable evidence lack credibility.  
**Consequences**: Added `RawEvidence`, `EvidenceSource`, `EvidenceTransformation`, and `FindingEvidenceLink` to domain model.

---

## 13. ADR-013: 5-Dimensional Risk Separation & Formula Versioning
**Decision**: Risk logic is split into 5 distinct dimensions (Technical, Data Exposure, Business Impact, Vendor, Attack Path) before weighted aggregation. Every finding output MUST stamp `risk_engine_version`.  
**Date**: 2026-08-13  
**Reason**: A single raw number obscures critical attack vectors. Versioning ensures historical audit reproducibility.  
**Consequences**: Risk engine refactored into dimensional evaluators; formula changes require explicit version bumps.

## ADR-016: In-Process Continuous Monitoring Scheduler & Fingerprint Deduplication
**Decision**: Continuous monitoring evaluation runs as a lightweight in-process thread-safe scheduler (`MonitoringScheduler`) with explicit overlap locking and deterministic SHA-256 fingerprint deduplication for in-app notifications. No distributed queues (Kafka, Celery) are introduced for the hackathon architecture.
**Date**: 2026-08-14
**Reason**: Maintains lightweight offline portability and strict determinism while providing complete continuous evaluation capabilities.
**Consequences**: Periodic evaluation runs safely in-process; notifications never spam identical alerts across polling cycles.

---

## 14. ADR-014: Structured Business Purpose Catalog Validation
**Decision**: Business purpose must be selected from a versioned, system-curated `BusinessPurposeCatalog` with explicit required/optional permission mappings. Free text is stored strictly for human audit notes and cannot be used as primary security input.  
**Date**: 2026-08-13  
**Reason**: Free-text declarations allow users to bypass least-privilege checks by writing arbitrary descriptions.  
**Consequences**: Implemented structured catalog mapping; excess detection algorithm executes set difference against catalog permissions.

---

## 15. ADR-015: 4-Stage Bounded AI Prompt Injection Pipeline
**Decision**: All third-party metadata injected into Gemini LLM prompts MUST pass through a 4-stage isolation pipeline (Sanitize -> Bounded JSON Context -> Hardened System Prompt -> Sanitized Output Display).  
**Date**: 2026-08-13  
**Reason**: Malicious OAuth application titles or scope descriptions could execute indirect prompt injection to alter AI explanations.  
**Consequences**: Added Pydantic sanitization filters and JSON parameter bounding for all AI calls.

---

## 16. ADR-016: HttpOnly Cookie Transport & Database-Backed Session Revocation
**Decision**: JWT tokens for browser clients MUST be transported via `HttpOnly`, `SameSite=Lax` cookies rather than `localStorage`. Server-side session state is tracked in `UserSession` table; revocation (`logout`) marks `revoked_at` timestamp.  
**Date**: 2026-08-13  
**Reason**: Storing JWTs in `localStorage` exposes session bearer tokens to XSS credential extraction.  
**Consequences**: Updated `/auth/login` and `/auth/logout` endpoints to issue/clear HttpOnly cookies. `get_current_user` inspects cookie first, with Bearer header fallback for API tests.

---

## 17. ADR-017: Post-Issuance DB Role Validation & Login Abuse Protection
**Decision**: Authorization checks (`require_role`, `get_current_org_id`) MUST query current user database state on every request rather than trusting unvalidated JWT payload claims. Failed logins are throttled (5 attempts -> 15 min lock).  
**Date**: 2026-08-13  
**Reason**: Relying purely on JWT claims allows suspended users or downgraded roles to retain elevated access until token expiration.  
**Consequences**: Implemented dynamic DB role check and account locking logic in user authentication flow.

---

## 18. ADR-018: Double-Defense Anti-CSRF Architecture & Origin Verification
**Decision**: All state-changing API endpoints (`POST`, `PATCH`, `DELETE`, `PUT`) MUST enforce SameSite cookie policy AND server-side Origin / `X-Requested-With` header verification. Cross-origin state-changing requests are rejected with `403 Forbidden`.  
**Date**: 2026-08-13  
**Reason**: Relying solely on `HttpOnly` cookies leaves applications vulnerable to CSRF if `SameSite` policies are bypassed or misconfigured.  
**Consequences**: Added CSRF middleware in `main.py` and `X-Requested-With: XMLHttpRequest` headers in frontend `api.ts`.

---

## 19. ADR-019: Production Fail-Closed Startup Validation & Zero-Token Storage
**Decision**: In production mode (`DEMO_MODE=False`), AccessGuard MUST fail closed on startup if `SECRET_KEY` is weak or `COOKIE_SECURE=False`. The frontend MUST NOT store tokens in `localStorage` or `sessionStorage`.  
**Date**: 2026-08-13  
**Reason**: Storing JWTs in browser storage exposes credentials to XSS. Insecure production defaults lead to compromised deployments.  
**Consequences**: Added configuration validation in `config.py` and refactored `AuthContext.tsx` to rely strictly on HttpOnly cookies.

---

## 20. ADR-020: Provider-Neutral Connector Boundary & Architectural Read Guard
**Decision**: All live third-party integrations MUST inherit from `BaseConnector` enforcing an architectural read guard (`READ=True, WRITE=False`). Any attempt to invoke write methods (`revoke_permission`, `modify_resource`) raises `NotImplementedError`.  
**Date**: 2026-08-13  
**Reason**: To guarantee that live connector exploration cannot accidentally modify external SaaS provider configurations during investigation phases.  
**Consequences**: Added `BaseConnector`, `ConnectorCapabilities`, and write-guard logic in `app/connectors/base.py`.

---

## 21. ADR-021: Environment Secret Management & Conservative Unknown Normalization
**Decision**: Connector secrets (GitHub App PEM keys, OAuth tokens) MUST be managed strictly via environment variables. Raw payloads MUST redact credential keys (`[REDACTED]`) before database insertion. Unknown provider permissions MUST map to `CanonicalPermission.UNKNOWN` with `HIGH` severity.  
**Date**: 2026-08-13  
**Reason**: Storing credentials in databases creates severe breach vectors. Silently mapping unknown scopes to `READ` creates invisible risk.  
**Consequences**: Implemented `redact_secrets()` in `normalization.py` and conservative unknown permission mapping.

---

## 22. ADR-022: Strict Separation of Supplier Posture Risk from Application Access Risk
**Decision**: Supplier due diligence risk (NIST SP 1326 FOCI, Provenance, Resilience, Foundational Cyber Practices) MUST be computed by a dedicated `SupplierRiskEngine` and displayed independently from Application Access Risk (`RiskEngine v1.5.0`). Favorable supplier due diligence MUST NEVER suppress or reduce high permission or crown jewel exposure risk.
**Date**: 2026-08-14  
**Reason**: Conflating supplier certification posture with actual technical scope access creates false assurance and obscures dangerous privilege escalation.  
**Consequences**: Implemented `SupplierRiskEngine`, `SupplierProfile`, `SupplierDueDiligence`, `SupplierSubprocessor`, and versioned assessment history in `app/models/vendor.py`.

