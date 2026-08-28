# 09 — Implementation Scope (Hardened)
# AccessGuard: Hackathon Scope & Phase 1 Execution Plan

**Document Type:** Implementation Scope  
**Version:** 1.5  
**Date:** 2026-08-13  
**Status:** Approved Implementation Blueprint  

---

## 1. Scope Discipline Principles

To guarantee a reliable, production-quality hackathon delivery, AccessGuard strictly divides capabilities into three tiers:

- **CATEGORY A: MUST WORK (15 Core Capabilities)** — Fully functional, tested, integrated into main demo story.
- **CATEGORY B: SHOULD WORK IF STABLE (6 Stretch Capabilities)** — Implemented only if Category A unit and integration tests pass cleanly.
- **CATEGORY C: ARCHITECTURE & ROADMAP ONLY (10 Future Capabilities)** — Documented in architecture specifications; UI marks as "Roadmap".

---

## 2. Category A — MUST BE FULLY WORKING (15 Core Features)

| Feature | Description | Implementation Target |
|---|---|---|
| **A1. Application Inventory** | Filterable/searchable inventory with status badges (Active, Dormant, Shadow, Revoked) | FastAPI CRUD + React Compact Table |
| **A2. Permission Mapping** | Normalized, human-readable permission catalog with severity labels | Scope Normalization Engine + JetBrains Mono formatting |
| **A3. Excess Permission Detection** | Gap analysis comparing granted scopes against `BusinessPurposeCatalog` | Set difference algorithm + excess ratio calculation |
| **A4. 5-Dimensional Risk Engine** | Deterministic calculation of TR, DER, BIR, VSR, and APR scores | `v1.5.0` pure Python evaluator + test vector suite |
| **A5. Explainable Risk Scoring** | Factor-by-factor score decomposition display in inspection drawer | Factor breakdown JSON API + AG-DS side drawer |
| **A6. Data-Flow Visualization** | Interactive node-edge graph mapping apps to permissions and data assets | React Flow graph presentation layer |
| **A7. Attack-Path Analysis** | Graph traversal identifying potential access paths to crown-jewel assets | Server-side Python BFS/DFS traversal engine |
| **A8. Blast-Radius Calculation** | Quantitative set intersection calculation of exposed assets and departments | Server-side graph analysis module |
| **A9. What-If Simulation** | Pre-calculation of score reduction if specific permissions are revoked | In-memory risk engine simulation + Amber UI banner |
| **A10. Remediation Workflows** | 8-State lifecycle tracking finding state from `NEW` to `CLOSED` | State machine transitions + explicit "SIMULATION ONLY" tag |
| **A11. Vendor Risk Aggregation** | Vendor trust scores, SOC 2 status, breach history, aggregate app risk | Vendor domain model + risk aggregator |
| **A12. Data Asset Inventory** | Named organizational data assets classified by sensitivity (PII, Financial) | DataAsset domain model + reverse application lookup |
| **A13. Immutable Evidence Logging** | Traceability from finding to raw payload hash, timestamp, and connector source | `RawEvidence` & `FindingEvidenceLink` models |
| **A14. Audit Report Generation** | PDF report export for leadership/auditors with evidence summary | WeasyPrint HTML-to-PDF template generator |
| **A15. SecOps Dashboard** | High-density dashboard with posture score, trend history, top findings | AG-DS Dashboard with compact filters and risk summary |

---

## 3. Category B — SHOULD WORK IF STABLE (6 Stretch Features)

1. **B1. AI Security Analyst**: Bounded, advisory chat interface (Gemini 2.0 Flash) for natural language Q&A.
2. **B2. Policy Engine**: Simplified rule evaluator (5 built-in policy rules).
3. **B3. Google Workspace Connector**: Live API connector using domain-wide service account.
4. **B4. Permission-Change Velocity Alerting**: Delta detection tracking permission expansions over time.
5. **B5. Shadow SaaS Auto-Detection**: Heuristic flagging of unauthorized OAuth apps.
6. **B6. Compliance Reference Mapping**: Mapped control references for SOC 2 Trust Services Criteria & ISO 27001.

---

## 4. Category C — ARCHITECTURE ONLY (10 Roadmap Features)

1. **C1. Full Connector Suite** (Microsoft 365, GitHub, Slack, AWS).
2. **C2. Behavioral Anomaly Detection** (ML access frequency baselining).
3. **C3. Fourth-Party Supply-Chain Deep Analysis** (Vendor sub-processor graphing).
4. **C4. Policy-as-Code Engine** (OPA / Rego DSL integration).
5. **C5. Multi-Party Approval Workflows** (Multi-sig remediation authorization).
6. **C6. Full SOAR Webhook Execution** (Automated API revocation).
7. **C7. Third-Party Assessment Questionnaire Module**.
8. **C8. Real-Time Security Event Streaming**.
9. **C9. Custom RBAC Role Builder**.
10. **C10. Scenario Simulation for Uninstalled Apps**.

---

*Implementation Scope v1.5 — Approved Execution Plan.*
