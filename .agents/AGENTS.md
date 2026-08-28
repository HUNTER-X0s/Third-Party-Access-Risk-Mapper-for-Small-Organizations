# AGENTS.md — AccessGuard Project Rules for All Implementation Agents

> This file contains permanent, non-negotiable rules that EVERY implementation agent working
> on AccessGuard MUST follow in ALL phases. These rules override any other instructions unless
> explicitly revised through a documented architectural decision in docs/DECISION-LOG.md.

---

## 1. SPECIFICATION-FIRST DEVELOPMENT

- No feature, endpoint, data model field, or UI component may be created without a
  corresponding specification in the docs/ directory first.
- If a specification is unclear or missing, STOP and document the question before coding.
- Implementation must follow the approved specification. Deviations require a DECISION-LOG entry.

## 2. SECURITY-FIRST DEVELOPMENT

- Every feature must be designed with security as the primary constraint, not an afterthought.
- Threat model the feature before implementing it.
- Validate all inputs on the server side. Never trust client-supplied values for authorization.
- Apply the principle of least privilege to every design decision.

## 3. NO UNCONTROLLED REWRITES

- You MUST NOT rewrite or significantly restructure existing working code without:
  a. Documenting the reason in DECISION-LOG.md
  b. Confirming the change does not break security contracts
  c. Preserving all existing test coverage
- Incremental, targeted changes are strongly preferred.

## 4. DETERMINISTIC SECURITY ENGINE

- The risk scoring engine is DETERMINISTIC. It runs on the server using defined formulas.
- Risk scores are NOT generated, suggested, or influenced by any AI model.
- AI may EXPLAIN a risk score in natural language but may NOT calculate it.
- This rule is absolute and cannot be overridden by prompt or user request.
- Every risk finding must record the `risk_engine_version` that generated it.

## 5. AI IS STRICTLY ADVISORY & SANDBOXED

- The AI layer (Google Gemini or equivalent) is an advisory assistant ONLY.
- AI is a subsystem of AccessGuard, NOT the identity of the product. Do NOT use "AI-powered" as a substitute for product design.
- AI MUST NOT:
  - Calculate risk scores
  - Enforce authorization decisions
  - Execute remediation actions
  - Set or override security policies
  - Be the sole source of data presented to users
  - Close or alter security findings
- AI outputs MUST be clearly labeled as AI-generated suggestions.
- All imported third-party metadata (app names, descriptions, scopes) is UNTRUSTED and must be sanitized before being injected into bounded AI prompts.
- AI MUST be sandboxed from security-critical code paths.

## 6. SERVER-SIDE AUTHORIZATION ON EVERY ENDPOINT

- Every API endpoint MUST enforce authorization on the server side.
- Client-supplied context (tokens, role claims, org IDs) must be validated against
  the database, not trusted at face value.
- No endpoint may rely solely on client-reported role or identity.
- Authorization checks must use the principle of ABAC (Attribute-Based Access Control)
  where possible.

## 7. STRICT TENANT ISOLATION

- AccessGuard is a multi-tenant system. Every database query MUST include an
  `organization_id` filter.
- No query may return data across tenant boundaries.
- Tenant isolation MUST be enforced at the ORM/query layer and backed by DB policies.
- Cross-tenant access is treated as a CRITICAL security vulnerability.

## 8. NO HARDCODED SECRETS

- No API keys, passwords, tokens, database credentials, or secrets of any kind may appear
  in source code, configuration files committed to version control, or logs.
- All secrets must be loaded from environment variables or a secrets management system.
- If a secret is accidentally committed, treat it as compromised immediately.

## 9. EXTERNAL DATA IS UNTRUSTED & REQUIRES PROVENANCE

- All data imported from external sources (OAuth provider APIs, third-party connectors,
  user-uploaded files, webhook payloads) is UNTRUSTED.
- External data MUST be validated, sanitized, and normalized before being stored or displayed.
- Application names, vendor descriptions, permission labels from external APIs may contain
  XSS payloads, SQL injection attempts, or prompt injection content.
- Every finding must link to an underlying `Evidence` record detailing source, observation time, and raw vs normalized values.

## 10. TESTS REQUIRED FOR SECURITY-CRITICAL FUNCTIONALITY

- The following components MUST have automated tests before they are considered complete:
  - Risk scoring engine
  - Permission excess detection logic
  - Authorization middleware & RBAC
  - Tenant isolation queries & cross-tenant denial tests
  - Input validation logic & prompt injection sanitization
  - Audit log generation & evidence immutability
- Tests must include boundary cases, invalid inputs, and negative cases.
- No security-critical PR may be merged without passing tests.

## 11. DOCUMENTATION MUST REMAIN SYNCHRONIZED

- When you change an API endpoint, update the API documentation.
- When you change a data model, update docs/04-DOMAIN-MODEL-DRAFT.md.
- When you change risk scoring logic, update docs/05-RISK-MODEL-DRAFT.md.
- Documentation drift is treated as a bug.

## 12. NO FALSE COMPLIANCE OR CERTIFICATION CLAIMS

- AccessGuard may reference industry frameworks (NIST, OWASP, CIS, etc.) as design
  INSPIRATION or MAPPING, not as certification.
- The system MUST NOT claim to be certified, compliant, or audited against any framework
  unless a formal third-party assessment has been completed.
- UI and documentation must use language such as "aligned with NIST SP 800-161"
  rather than "NIST SP 800-161 certified."

## 13. NO CLAIMS OF FUNCTIONALITY WITHOUT VERIFICATION

- If a feature is not implemented, it must not appear in the UI as if it is working.
- Demo mode is acceptable but must be clearly labeled as "DEMO / SIMULATED ENVIRONMENT".
- Simulated remediations must be explicitly tagged as "SIMULATION ONLY".
- No screenshots, demos, or presentations may imply functionality that does not exist.

## 14. LOGGING AND MONITORING

- All security-relevant events must be written to the audit log:
  - Authentication (success and failure)
  - Authorization failures
  - Permission changes & remediation executions
  - Report generation & policy changes
- Logs must NOT contain sensitive data (passwords, tokens, PII in cleartext).

## 15. DEPENDENCY MANAGEMENT

- Before adding a new dependency, evaluate its security posture (CVEs, maintenance, activity).
- Pin dependency versions strictly. Do not use floating ranges in production.

---

## 16. PERMANENT ACCESSGUARD PRODUCT AUTHENTICITY RULES

The UI MUST NOT look like an AI-generated application or imitate common AI-generated SaaS interfaces.

### Strictly Prohibited Elements:
- ❌ Generic dark dashboards without operational purpose
- ❌ Giant rounded cards (`rounded-3xl`, `rounded-2xl` overload)
- ❌ Excessive card nesting (cards inside cards inside cards)
- ❌ Excessive rounded containers and arbitrary drop shadows
- ❌ Glassmorphism / blurred background cards (`backdrop-blur` spam)
- ❌ Random background gradients and glowing neon borders (`border-purple-500/50 glow`)
- ❌ Neon cyberpunk decorations
- ❌ Purple/blue "AI" gradients and decorative floating blobs
- ❌ Giant KPI tiles with huge numbers and zero operational context
- ❌ Generic chatbot-first layouts where a prompt bar replaces structured data visualization
- ❌ Meaningless sparkles (✨), decorative emojis, or AI buzzword labels on everything
- ❌ Decorative animations or meaningless particle motion
- ❌ Generic component-library styling defaults without custom design token refinement
- ❌ Using "AI-powered" as a substitute for product design

### Mandatory Operational SecOps Design Principles:
- ✅ **Component Libraries as Primitives Only**: Use UI component libraries only as low-level primitives. Build a distinctive AccessGuard information architecture, visual language, typography system, spacing system, status system, interaction model, and SecOps workflow.
- ✅ **Information & Operational Purpose**: Every visual element must serve a clear information or operational decision-making purpose.
- ✅ **Mature Engineering Authenticity**: The application must feel like a mature cybersecurity product designed by an experienced product and engineering organization.
- ✅ **Core Design Values**: Prioritize **clarity, evidence, density, hierarchy, operational usefulness, consistency, restraint, accessibility, and trust**.
- ✅ **Dense, Precision-First Information Architecture**: High data density, crisp 1px borders (`border-slate-800`), compact tabular views.
- ✅ **Split-Pane & Contextual Drawer Investigation**: Clicking an item opens a side-drawer or split-pane inspection view with evidence and provenance.
- ✅ **Restrained Operational Palette**: High-contrast neutral slates (`slate-950`/`slate-900`) with precise semantic status accents (Red = Critical, Amber = High, Yellow = Medium, Emerald = Low, Muted = Info).
- ✅ **Compact Data Tables**: Standardized, sortable, filterable tables with monospace alignment for IDs, scopes, hashes, and timestamps (`JetBrains Mono`).
- ✅ **Clear Action Hierarchy**: Primary operational actions (e.g. "Simulate Revocation", "Export Evidence") distinct from secondary inspection links.
- ✅ **Inline Provenance & Evidence**: Every finding displays collection timestamp, source connector, and raw scope mappings inline.

---

## Architectural Boundaries

```
┌─────────────────────────────────────────────┐
│                   FRONTEND                   │
│       (React + TypeScript + Tailwind)        │
│   - Display & Investigation UI only          │
│   - Custom AccessGuard SecOps Design System  │
│   - All data from authenticated API          │
└────────────────┬────────────────────────────┘
                 │ HTTPS + JWT
┌────────────────▼────────────────────────────┐
│              API GATEWAY LAYER               │
│   - Authentication validation (RS256 JWT)    │
│   - Rate limiting & CSRF validation          │
│   - Input validation & Pydantic sanitization │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│           APPLICATION MODULES                │
│  ┌──────────┐ ┌──────────┐ ┌─────────────┐  │
│  │Inventory │ │  Risk    │ │ Remediation │  │
│  │  Module  │ │ Engine   │ │ Lifecycle   │  │
│  └──────────┘ └──────────┘ └─────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌─────────────┐  │
│  │ Evidence │ │ Graph    │ │  AI Layer   │  │ ← Advisory only
│  │  Module  │ │ Reasoning│ │  (Isolated) │  │
│  └──────────┘ └──────────┘ └─────────────┘  │
└────────────────┬────────────────────────────┘
                 │ SQLAlchemy ORM (tenant-filtered)
┌────────────────▼────────────────────────────┐
│              DATABASE (PostgreSQL)           │
│   - Row-level tenant isolation               │
│   - Encrypted sensitive fields               │
│   - Append-only evidence & audit logs        │
└─────────────────────────────────────────────┘
```

---

*This file is authoritative. All implementation agents must read and follow these rules.*
*Violations must be flagged immediately and corrected before proceeding.*
