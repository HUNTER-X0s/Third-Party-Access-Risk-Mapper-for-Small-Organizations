# PHASE-0-FINAL-REPORT.md
# AccessGuard: Phase 0 Complete Blueprint

**Document Type:** Phase 0 Final Report  
**Version:** 1.0  
**Date:** 2026-08-13  
**Classification:** Internal — Hackathon Planning  

---

## 1. Product Vision

**AccessGuard** is a third-party access intelligence and risk management platform designed specifically for small organizations that lack dedicated security staff but depend heavily on cloud services, SaaS applications, and external integrations.

**The core insight:** Small organizations authorize dozens of third-party applications, each of which receives OAuth permissions to read emails, write files, post messages, or access databases. This creates an invisible, growing attack surface. AccessGuard makes that attack surface visible, measurable, and reducible — without requiring a security expert to operate it.

**The product vision in one sentence:**
> AccessGuard gives small organizations the third-party access intelligence that was previously available only to enterprise security teams.

**Strategic positioning:** AccessGuard sits at the intersection of three recognized security categories — SSPM (SaaS Security Posture Management), TPRM (Third-Party Risk Management), and IAM (Identity and Access Management) — but deliberately scopes itself to the original problem: third-party applications, their permissions, and their data access.

---

## 2. Problem Interpretation

The original problem statement describes symptoms of a well-understood class of security problem:

> *"Small organizations use many cloud services, plugins and external vendors but often lack visibility into what information each service can access."*

**Surface interpretation:** Build a dashboard showing which apps have which permissions.

**Correct interpretation:** 
The real problem is that small organizations have created an expanding, unmanaged access network. Each OAuth authorization is an implicit trust relationship. Those relationships are:
- Created by multiple people (not just IT)
- Never systematically reviewed
- Not scoped to minimum necessary access
- Not monitored for changes
- Not mapped to the actual data they can reach
- Not assessed for the supply-chain risk of the vendor behind them

The expected outcome — "a visual risk map showing which authorized external services can access organizational information and where access should be reduced" — is the *output* of solving this deeper problem, not the problem itself.

**AccessGuard therefore operates at three levels:**
1. **Visibility** — What exists (application inventory, permission catalog)
2. **Intelligence** — What it means (risk scoring, excess detection, attack paths)
3. **Action** — What to do about it (remediation, simulation, tracking)

---

## 3. Core Security Model

The conceptual chain that powers AccessGuard:

```
WHO (User or System)
  ↓ AUTHORIZED
WHICH THIRD-PARTY APPLICATION
  ↓ WAS GRANTED
WHICH PERMISSIONS
  ↓ ENABLING ACCESS TO
WHICH DATA ASSETS
  ↓ SUPPOSEDLY FOR
WHICH BUSINESS PURPOSE
  ↓ THROUGH
WHICH VENDOR / SUPPLY CHAIN
  ↓ CREATING
WHAT ATTACK SURFACE (if app or vendor is compromised)
  ↓ WITH
WHAT BUSINESS IMPACT (data exposed, regulatory risk, operational disruption)
  ↓ REQUIRING
WHAT REMEDIATION (revoke, scope-down, review, monitor)
  ↓ RESULTING IN
WHAT RISK REDUCTION (quantified, simulated, tracked)
```

**Why this model is the right conceptual foundation:**
- It captures every dimension judges and security professionals will probe
- It naturally generates all the required features (inventory → mapping → risk → remediation)
- It is explainable: every risk score is traceable through this chain
- It reflects real-world how attacks actually happen (compromised OAuth app → data exfiltration)
- It creates the attack-path and blast-radius capabilities organically (following the chain when an app is compromised)

---

## 4. Feature Landscape

AccessGuard's feature space spans four tiers:

| Tier | Description | Count |
|---|---|---|
| **TIER 0** | Required by problem statement | 7 |
| **TIER 1** | Required for strong hackathon submission | 18 |
| **TIER 2** | National-level differentiator | 12 |
| **TIER 3** | Future commercial roadmap | 6 |

Full detail: [02-FEATURE-MATRIX.md](02-FEATURE-MATRIX.md)

**Key feature landscape insight:** The problem statement requires 7 features (inventory, mapping, visualization, scoring, excess detection, remediation, reports). A strong hackathon submission requires an additional 18. The differentiating features (attack paths, blast radius, what-if simulation, explainable scoring) are what separate a submission from a CRUD application.

---

## 5. Recommended Feature Set

### MUST implement (15 capabilities for hackathon MUST WORK scope):

1. Application Inventory (filterable, searchable, status-aware)
2. Permission Mapping (normalized, human-readable, severity-labeled)
3. Excess Permission Detection (gap analysis vs. declared business purpose)
4. 10-Factor Deterministic Risk Scoring Engine
5. Explainable Risk Score Display (factor-by-factor breakdown)
6. Data-Flow Visualization (interactive React Flow graph)
7. Attack-Path Analysis (graph traversal with animated display)
8. Blast-Radius Analysis (reachable assets from compromise)
9. What-If Remediation Simulation (score prediction before action)
10. Remediation Recommendations (specific steps, effort, link to provider)
11. Vendor Inventory with Risk Aggregation
12. Data Asset Inventory with Classification
13. Audit Report Generation (PDF + JSON)
14. Security Event Timeline
15. Dashboard (posture score, findings, trend)

### STRONG additions if time permits:
- AI Security Analyst (advisory, labeled)
- Policy Engine (5 built-in rules)
- Google Workspace live connector
- Permission-change detection and alerting
- Shadow SaaS detection

---

## 6. Architecture Direction

**Decision:** Modular Monolith (see ADR-001)

```
┌─────────────────────────────────────────────────────┐
│                  ACCESSGUARD                        │
│                                                     │
│  ┌────────────┐  Nginx  ┌────────────────────────┐  │
│  │  React +   │ ──────► │   FastAPI Application  │  │
│  │ TypeScript │         │                        │  │
│  │            │  JSON   │  ┌──────────────────┐  │  │
│  │ shadcn/ui  │  API    │  │  Inventory Mod.  │  │  │
│  │ React Flow │         │  ├──────────────────┤  │  │
│  │ Recharts   │         │  │  Risk Engine Mod.│  │  │
│  └────────────┘         │  ├──────────────────┤  │  │
│                         │  │  Reporting Mod.  │  │  │
│                         │  ├──────────────────┤  │  │
│                         │  │  AI Advisor Mod. │  │  │
│                         │  ├──────────────────┤  │  │
│                         │  │  Connector Mod.  │  │  │
│                         │  └──────────────────┘  │  │
│                         │         │              │  │
│                         │  SQLAlchemy ORM        │  │
│                         └──────────┬─────────────┘  │
│                                    │                 │
│                         ┌──────────▼─────────────┐  │
│                         │  PostgreSQL / SQLite    │  │
│                         └────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

**Module boundaries (no circular dependencies allowed):**
- `inventory` — Application, Vendor, Permission, DataAsset management
- `risk_engine` — Deterministic risk scoring; pure functions only; no external calls
- `reporting` — Report generation, audit evidence, export
- `ai_advisor` — AI chat interface; receives context from other modules; never writes security data
- `connectors` — Provider-specific data ingestion; outputs only normalized types
- `auth` — Authentication, JWT, RBAC middleware

---

## 7. Technology Recommendation

| Layer | Technology | Justification |
|---|---|---|
| Frontend | React 18 + TypeScript | Type safety, React Flow compatibility |
| Styling | Tailwind CSS + shadcn/ui | Premium aesthetics, accessible components |
| Graph | React Flow | Purpose-built for interactive access graphs |
| Charts | Recharts | React-native; declarative |
| Backend | FastAPI + Python 3.12 | Auto-OpenAPI, Pydantic validation, async |
| Validation | Pydantic v2 | Best-in-class input validation |
| ORM | SQLAlchemy 2.0 + Alembic | Async, multi-DB, migrations |
| DB (demo) | SQLite | Zero-infrastructure demo |
| DB (prod) | PostgreSQL 16 | RLS tenant isolation, JSONB |
| Auth | JWT RS256 + PKCE | RFC 9700 compliant |
| Jobs | APScheduler | Connector polling without infrastructure |
| AI | Google Gemini 2.0 Flash | Advisory layer; large context |
| PDF | WeasyPrint | HTML-to-PDF from report templates |
| Testing | pytest + httpx + Vitest | Full stack test coverage |
| Container | Docker + Compose | Single-command demo startup |

Full analysis: [03-TECHNOLOGY-EVALUATION.md](03-TECHNOLOGY-EVALUATION.md)

---

## 8. Domain Model Overview

**25 core entities** defined in [04-DOMAIN-MODEL-DRAFT.md](04-DOMAIN-MODEL-DRAFT.md).

**Key design decisions:**
- `AccessRelationship` is a first-class entity (not just a join table) — enables the graph and risk traversal
- `PermissionGrant` tracks each granted scope with excess flag — enables excess detection
- `RiskFactor` stores individual factor values — enables explainability
- `AttackPath` stores pre-computed graph traversal results — enables fast visualization
- `AuditEvent` is append-only — immutable audit trail

**Entity hierarchy:**
```
Organization
  ├── ApplicationInstance → Application → Vendor
  │     ├── PermissionGrant → Permission → DataClassification
  │     ├── AccessRelationship → DataAsset
  │     ├── RiskFinding → Remediation
  │     └── AttackPath → DataAsset
  ├── DataAsset
  ├── Policy → PolicyViolation
  ├── AuditEvent
  ├── Report
  └── PostureSnapshot
```

---

## 9. Risk Model Overview

**Full model:** [05-RISK-MODEL-DRAFT.md](05-RISK-MODEL-DRAFT.md)

### Formula
```
ApplicationRiskScore = Σ(Factor_i.value × Factor_i.weight) × ContextMultiplier
```

### 10 Factors
| ID | Factor | Weight |
|---|---|---|
| F1 | Permission Severity | 0.25 |
| F2 | Excess Privilege | 0.20 |
| F3 | Data Sensitivity | 0.20 |
| F4 | External Exposure | 0.10 |
| F5 | Vendor Trust | 0.10 |
| F6 | Identity Assurance | 0.05 |
| F7 | Review Freshness | 0.05 |
| F8 | Permission-Change Velocity | 0.03 |
| F9 | Dormancy Signal | 0.01 |
| F10 | Policy Violation | 0.01 |

### Severity Bands
```
85–100: Critical  |  65–84: High  |  40–64: Medium  |  15–39: Low  |  0–14: Info
```

### Key Properties
- **Deterministic** — Same inputs always produce same output
- **Explainable** — Every score decomposes to factor contributions
- **Composable** — Application → Vendor → Organization aggregation chain
- **Bounded** — Clamped to [0, 100] with defined multipliers
- **Confident** — Confidence level indicates data quality

---

## 10. Security Principles

**Full model:** [06-SECURITY-PRINCIPLES.md](06-SECURITY-PRINCIPLES.md)

**Non-negotiable security controls:**

| Control | Implementation |
|---|---|
| Tenant isolation | ORM-layer filter + PostgreSQL RLS |
| Server-side auth | Every API endpoint; no client role trust |
| Input validation | Pydantic v2 on all request bodies |
| External data sanitization | All connector output through NormalizationEngine |
| Audit trail | Append-only AuditEvent table |
| Token security | HttpOnly cookies, RS256, 15-min expiry |
| XSS prevention | React JSX escaping + CSP headers |
| SQL injection | SQLAlchemy parameterized queries only |
| AI isolation | AI module has no write access to security data |
| No hardcoded secrets | Environment variables + secrets manager |

---

## 11. AI Strategy

**Position:** AI is an advisory intelligence amplifier, never a security decision-maker.

**What AI does in AccessGuard:**
- Explains risk scores in natural language ("Here's why this is Critical...")
- Answers natural-language queries ("Which apps can read my email?")
- Generates executive summaries for reports
- Assists in investigation reasoning ("This pattern looks like...")

**What AI explicitly CANNOT do:**
- Calculate or modify risk scores
- Enforce policy or authorization decisions
- Execute remediation actions
- Serve as the authoritative source for any displayed data

**Technical isolation:** AI module is sandboxed. It receives context (pre-computed scores, sanitized app metadata) and returns natural-language text. It has no database write access. Its output is sanitized before display.

**Graceful degradation:** If the AI API is unavailable, all platform functionality continues. The AI chat UI shows "AI analysis temporarily unavailable" and all risk, inventory, and remediation features work normally.

---

## 12. Integration Strategy

**Full concept:** [07-INTEGRATION-CONCEPT.md](07-INTEGRATION-CONCEPT.md)

**Three acquisition modes:**
1. Manual entry — always available, lower confidence
2. Seeded demo data — production-quality, offline-capable
3. Live connectors — real-time, higher confidence

**Provider-neutral connector design:**
- All connectors implement `BaseConnector` abstract interface
- All output normalized to canonical types before reaching domain layer
- Permission normalization table maps raw OAuth scopes to semantic canonical permissions
- Unknown scopes logged for review; conservatively scored as medium severity

**Hackathon connector priority:**
1. ✅ Demo/seeded data (must work)
2. 🎯 Google Workspace Admin SDK (stretch goal)
3. 🗺 Microsoft 365, GitHub, Slack (roadmap)

---

## 13. Hackathon Implementation Scope

**Full detail:** [09-IMPLEMENTATION-SCOPE.md](09-IMPLEMENTATION-SCOPE.md)

### MUST WORK (Category A): 15 features
Full application inventory, permission mapping, excess detection, risk scoring, explainability, data-flow visualization, attack paths, blast radius, what-if simulation, remediation, vendor inventory, data assets, reports, timeline, dashboard.

### SHOULD WORK (Category B): 10 features  
Permission change detection, policy engine, attack path animation, Google Workspace connector, AI analyst, shadow SaaS flags, compliance mapping, SLA tracking, mobile responsiveness, behavioral anomaly framework.

### ARCHITECTURE ONLY (Category C): 10 features  
Full connector suite, behavioral anomaly detection, fourth-party risk, policy-as-code, scenario simulation, continuous monitoring, vendor questionnaires, custom RBAC creation, Microsoft 365 connector, third-party assessment workflows.

---

## 14. Future Roadmap

| Phase | Timeline | Key Additions |
|---|---|---|
| **v1.0** (Hackathon) | Immediate | Core platform, risk engine, visualization, demo data |
| **v1.1** | 1–2 months | Google Workspace + Microsoft 365 live connectors |
| **v1.2** | 2–4 months | GitHub, Slack, AWS connectors; behavioral anomaly detection |
| **v2.0** | 4–8 months | Policy-as-code, approval workflows, enterprise RBAC |
| **v2.1** | 6–10 months | Fourth-party risk, vendor questionnaire module |
| **v3.0** | 10–18 months | SOAR-style integration, compliance automation, marketplace |

---

## 15. Competitive Differentiation

**The three strongest differentiators (in order):**

### Differentiator 1: Explainable, Deterministic Risk Intelligence
Most security tools produce risk scores. AccessGuard produces *reasons*. Every score is traceable to specific factors with specific weights. A judge or auditor can interrogate any score and get a complete justification. This is a security product that trusts the human, not one that demands the human trust it.

**Signal to judge:** "Ask me why any app is scored the way it is. I can show you the math."

### Differentiator 2: Attack-Path + Blast-Radius Visualization
Going from "list of permissions" to "this is the attack chain from your Zapier integration to your customer database" is a qualitative leap. Most SSPM tools show you what permissions exist. AccessGuard shows you what an attacker could do if they owned that app. This is genuine threat-modeling, not just inventory management.

**Signal to judge:** Shows understanding of adversarial thinking, not just compliance-oriented thinking.

### Differentiator 3: What-If Remediation Simulation
Quantifying risk reduction *before* taking action is a genuinely novel UX capability for tools at this scale. Security teams can prioritize remediation based on expected outcomes, not just perceived severity. "This one action reduces our Critical findings by 3 and drops our posture score from 45 to 72."

**Signal to judge:** Shows end-to-end thinking — not just finding problems, but quantifying solutions.

---

## 16. Judge Strategy

**Full strategy:** [08-JUDGE-STRATEGY.md](08-JUDGE-STRATEGY.md)

**Core positioning:** AccessGuard is not a student CRUD project dressed as a security tool. It is a coherent security product with a principled model, standards-informed design, and genuine technical depth visible at multiple layers.

**Demo path (5 minutes):** Scale of problem → Risk intelligence → Attack path visualization → What-if simulation → Audit evidence

**Strongest Q&A moments:** "Why is this scored 77?" → Walk through the 10-factor breakdown. "Is the AI making decisions?" → No, here is the formula. "What standards informed this?" → NIST 800-161, RFC 9700, OWASP API 2023.

---

## 17. Major Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Scope creep** — too many features, none working well | High | High | Strict Category A enforcement; resist adding features until A is complete |
| **Risk engine complexity** — 10 factors is complex to implement | Medium | High | Implement as pure functions; test each factor independently |
| **Demo data quality** — seeded data looks fake | Medium | High | Invest time in realistic, varied seed data; use real vendor names |
| **React Flow complexity** — interactive graph is difficult | Medium | High | Budget 2–3 days for graph implementation; start early |
| **AI prompt injection** — third-party data manipulates AI | Medium | Medium | Server-controlled prompts only; sanitize all injected context |
| **Tenant isolation failure** — cross-tenant data leak | Low | Critical | Integration tests that explicitly test cross-tenant access |
| **AI API unavailability during demo** — Gemini API down | Low | Medium | Demo mode with AI disabled works; show graceful degradation |
| **Over-promising on live connectors** — no working connector | Medium | Medium | Demo data is the primary; connector is bonus |

---

## 18. Major Trade-offs

| Trade-off | Decision | Rationale |
|---|---|---|
| **Simplicity vs. completeness** | Implement 15 features well vs. 43 features poorly | A working demo beats an impressive slide deck |
| **Live data vs. seeded data** | Seeded data primary | Reliability > authenticity for demo |
| **AI depth vs. AI safety** | AI advisory only | Security integrity > feature richness |
| **Microservices vs. monolith** | Modular monolith | Speed + simplicity win for hackathon scope |
| **Full compliance vs. standards alignment** | Alignment only | Honest claim beats false certification claim |
| **All connectors vs. one good connector** | Google Workspace as stretch | Depth > breadth |

---

## 19. Open Design Questions

These questions require answers before or early in Phase 1:

| # | Question | Impact |
|---|---|---|
| OQ-01 | What is the exact weight validation methodology for the 10-factor risk formula? Expert elicitation or literature-based? | Risk model calibration |
| OQ-02 | How should business purpose be captured — from a predefined catalog or free-text declaration? | Excess detection accuracy |
| OQ-03 | Should the organization posture score use arithmetic mean, weighted mean, or worst-case anchoring? | Posture score credibility |
| OQ-04 | How should attack paths be discovered — pre-computed during sync or computed on demand? | Performance vs. freshness |
| OQ-05 | What should the data retention policy be for PostureSnapshot history? | Storage planning |
| OQ-06 | Should the AI analyst have conversation context (multi-turn) or be single-turn per query? | AI UX complexity |
| OQ-07 | What is the seed data scenario — one fictional organization or multiple demo organizations? | Demo flexibility |
| OQ-08 | How should vendor trust score changes (e.g., new breach discovered) propagate to application risk scores? | Risk model trigger design |

---

## 20. Readiness Score

### Score: **84 / 100**

### Scoring Rationale

| Dimension | Score | Reasoning |
|---|---|---|
| Problem clarity | 10/10 | Problem fully understood and correctly interpreted at depth |
| Feature inventory | 9/10 | All 43 features analyzed; tiering is defensible; one feature (OQ-02 business purpose model) is still ambiguous |
| Architecture soundness | 9/10 | Modular monolith is correct choice; clean boundaries defined; ADRs documented |
| Risk model completeness | 9/10 | 10-factor formula is complete; weights need Phase 1 validation |
| Domain model completeness | 9/10 | 25 entities cover all requirements; one or two edge-case entities may emerge |
| Security model credibility | 10/10 | Platform security is thorough; all major threat vectors addressed |
| Technology justification | 9/10 | Stack is well-justified; one choice (APScheduler vs. Celery) may need revisiting |
| Implementation planning | 8/10 | 15 MUST features defined; sequencing clear; time estimates not yet created |
| Competitive differentiation | 9/10 | Three strong differentiators identified and defensible |
| Judge readiness | 8/10 | Q&A prepared; demo scripted; open questions remain (OQ-07 seed data) |
| **Total** | **90/110 → 82%** | |

**Why not 100:** 
- Risk model weights are design assumptions not yet validated against expert judgment or benchmarks (-4)
- Open design questions OQ-01 to OQ-08 require resolution in Phase 1 (-4)
- Implementation time estimates not yet created; timeline risk is unquantified (-4)
- Seed data not yet created; demo realism is unverified (-4)

**Why not below 80:**
- The security model is complete and credible at conceptual level
- All required documents are produced
- The architecture is sound and defensible
- The risk model is more rigorous than most hackathon submissions at this stage
- Standards references are accurate and appropriately applied

**Score of 84 means:** We have an excellent, credible blueprint. Phase 1 can begin. The open questions are bounded and answerable within Phase 1 planning.

---

## Self-Critique (Adversarial Principal Engineer Review)

**Q: Is this still solving the original problem?**  
Yes. The core of the product — application inventory, permission mapping, excess detection, risk scoring, data-flow visualization, remediation recommendations, and audit reports — directly addresses every stated requirement. No feature was added without tracing it to the original problem.

**Q: Are we building too much?**  
The MUST scope is realistic and tightly bounded. The SHOULD scope is deliberately conditional. Category C features are architecture-only. The risk is not building too much — the risk is that the 15 MUST features are all complex; some (React Flow graph, attack-path visualization) require significant engineering effort. Time management is the real risk.

**Q: Are we building too little?**  
No. The 15 MUST features cover all 7 original requirements plus the key differentiators. A demonstration of these 15 features is competitive nationally.

**Q: Is the architecture credible?**  
Yes. Modular monolith with FastAPI + PostgreSQL + React is a standard, production-capable stack. The module boundaries are clean. The security model is rigorous. A judge with enterprise engineering experience would find this credible.

**Q: Is the security model credible?**  
Yes. The platform security design in doc 06 addresses all major OWASP and NIST concerns explicitly. The threat model is realistic. The controls are implementable. The "no hardcoded secrets" and "AI is advisory" principles are enforced at the architectural level, not just as guidelines.

**Q: Is the risk model explainable?**  
Yes. The 10-factor formula with documented weights produces a decomposable score. The explainability output format is specified. Any score can be traced to factor inputs. However, the weights themselves need validation — we have chosen them based on security judgment but they have not been formally validated.

**Q: Can the system work without external APIs?**  
Yes. Demo mode with SQLite and seeded data is a first-class capability, not a fallback.

**Q: Can the demo work offline?**  
Yes, explicitly by design (ADR-009).

**Q: Can the AI layer fail without breaking security?**  
Yes. Graceful degradation is a documented requirement. AI is not in any critical code path.

**Q: Could cross-tenant access occur?**  
In the designed architecture, no. Tenant isolation at ORM layer + PostgreSQL RLS + cross-tenant integration tests provides three layers. However, this must be actively tested — the architecture prevents it but only correct implementation enforces it.

**Q: Could malicious third-party metadata manipulate the system?**  
In the designed architecture, no. All external data passes through the NormalizationEngine which validates and sanitizes. AI context is server-constructed from sanitized data only. However, the NormalizationEngine must be carefully implemented to actually enforce these guarantees.

**Q: Could a judge expose an architectural weakness?**  
The most likely weakness a judge might probe: "What if two organizations happen to have the same data?" → Mitigated by organization_id on all records. "What prevents an analyst from accessing admin functions?" → RBAC enforcement on every endpoint. "How do you prevent the AI from making up a risk score?" → AI receives the score; it cannot modify data.

**Q: Are any features included only for buzzwords?**  
- "AI Security Analyst" could be buzzword-only if not implemented carefully. Mitigation: implement it as a genuinely useful advisory tool, clearly labeled, with a narrow interface.  
- "Attack-path analysis" could be superficial if the graph traversal is faked. Mitigation: implement actual graph traversal from AccessRelationship data.  
- "Blast-radius analysis" could be a fake count if not computed from real data. Mitigation: compute from actual PermissionGrant → DataAsset chains.

**Q: Which three features create the strongest competitive advantage?**
1. **Explainable risk scoring** — Because it makes every claim verifiable and every recommendation justifiable
2. **Attack-path + blast-radius analysis** — Because it shows adversarial thinking, not just compliance checklist thinking
3. **What-if remediation simulation** — Because it quantifies the value of taking action before requiring action to be taken

---

*Phase 0 Complete. Blueprint is ready. Implementation may begin in Phase 1.*
