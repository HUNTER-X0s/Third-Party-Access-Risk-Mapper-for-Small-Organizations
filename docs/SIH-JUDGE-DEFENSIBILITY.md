# SMART INDIA HACKATHON (SIH) JUDGE DEFENSIBILITY GUIDE
# AccessGuard: Adversarial Q&A, Proof of Depth & Evaluation Strategy

**Document Type:** Hackathon Strategy Guide  
**Version:** 1.0  
**Date:** 2026-08-13  
**Status:** Approved Competition Strategy  

---

## 1. Hackathon Evaluation Rubric Mapping

AccessGuard is structured to score maximum points across standard Smart India Hackathon (SIH) national cybersecurity evaluation criteria:

| SIH Evaluation Criterion | Weight | How AccessGuard Wins Maximum Marks | Proof of Technical Depth |
|---|---|---|---|
| **Novelty & Innovation** | 20% | Explainable Risk Engine + Blast-Radius Analysis + What-If Simulation | Deconstructs scores into 5 dimensions + 10 weighted factors; zero black box. |
| **Technical Depth** | 25% | Graph Reasoning Engine + RFC 9700 OAuth Scope Normalization + Evidence Model | Formal `Evidence` entities with SHA-256 payload hashes; server-side BFS/DFS graph algorithm. |
| **Feasibility & Practicality** | 20% | Tailored for SMBs with zero dedicated security staff; modular monolith architecture | Solves real-world SaaS sprawl; 100% offline-capable demo with production-quality seed data. |
| **Security & Privacy of Product** | 15% | Multi-tenant isolation; Pydantic sanitization; Prompt injection defense pipeline | PostgreSQL RLS + ORM filters + OWASP API Top 10 BOLA mitigation + AI sandboxing. |
| **User Experience & Presentation** | 20% | High-density SecOps Product UI (AG-DS); zero AI-template gimmicks | Compact tabular views, split-pane inspection drawers, monospaced technical context, clear action hierarchy. |

---

## 2. Adversarial Judge Q&A Strategy (15 Critical Questions)

### Q1: "Why is your risk score 84/100 and not 75 or 90?"
- **Answer**: "AccessGuard uses a deterministic 10-factor formula across 5 risk dimensions. In finding FND-104, score 84 is derived from: Technical Risk (Permission Severity: 75/100, Excess Ratio: 62.5%), Data Exposure Risk (PII Customer Records reachable, sensitivity 85/100), and Vendor Risk (Vendor lacks SOC 2 and had a 2023 breach). The score is stamped with `risk_engine_version: v1.5.0` and can be reconstructed from raw evidence."

### Q2: "How is this different from an IAM or OAuth consent dashboard?"
- **Answer**: "IAM dashboards show you *what permissions exist*. AccessGuard performs **Permission-to-Data Asset Mapping**, calculates **Blast Radius**, identifies **Excess Access** against a structured Business Purpose catalog, and simulates **Risk Reduction** before you revoke permissions."

### Q3: "How do you determine if a permission is excessive?"
- **Answer**: "We compare granted permissions against a structured, versioned `BusinessPurposeCatalog`. For example, an app assigned `EMAIL_CAMPAIGN_SEND` requires `send_email`. If it also holds `read_email`, the excess engine flags `read_email` as an unneeded risk driver (+35 score contribution)."

### Q4: "Where does the data come from? What if the provider API is down?"
- **Answer**: "Data is ingested via provider connectors (e.g. Google Workspace Admin SDK). Every sync creates an immutable `RawEvidence` snapshot. If a connector fails, AccessGuard operates on the last verified snapshot, clearly marking data freshness as `STALE` with timestamp evidence."

### Q5: "Can your AI model modify permissions or change risk scores?"
- **Answer**: "No. The AI layer (Gemini 2.0 Flash) is strictly advisory and sandboxed. It receives pre-calculated scores to explain in natural language. It has zero database write access and cannot override policy or execute remediations."

### Q6: "What happens if a vendor lies about their security posture?"
- **Answer**: "Vendor trust is one factor (F5) out of 10. Even if a vendor claims perfect compliance, excessive permissions or high data sensitivity will still trigger High/Critical risk scores."

### Q7: "How do you detect Shadow SaaS?"
- **Answer**: "We correlate authorized OAuth applications discovered via provider admin logs against the organization's Approved Application Catalog. Any authorized app lacking an approved admin entry is flagged as `SHADOW_APP` with a +0.30 Context Multiplier penalty."

### Q8: "How do you handle fourth-party (supply-chain) risk?"
- **Answer**: "Vendor profiles include a `fourth_party_dependencies` array and supply-chain depth score. If a primary vendor relies on an insecure sub-processor, that risk propagates into the Vendor Risk Dimension (VSR)."

### Q9: "Can your graph visualization scale to 1,000 applications?"
- **Answer**: "Yes. React Flow is only the rendering layer. The server-side Python engine computes attack paths using adjacency list BFS/DFS and returns pruned subgraphs. Viewport clustering ensures smooth 60 FPS rendering."

### Q10: "Why is this useful for small organizations without security teams?"
- **Answer**: "Small business owners cannot interpret raw OAuth scope strings like `https://www.googleapis.com/auth/gmail.readonly`. AccessGuard translates scopes into plain English ('Can read all employee emails') and provides a single prioritized 'Top 3 Fixes' action list with estimated risk reduction."

### Q11: "What happens if your external connector fails during a demo?"
- **Answer**: "AccessGuard has a first-class `DEMO_MODE` running on an offline-capable SQLite instance pre-loaded with an internally consistent multi-tier attack story."

### Q12: "How do you prevent cross-tenant data leakage in multi-tenancy?"
- **Answer**: "Tenant isolation is enforced at three layers: ORM-level mandatory `organization_id` query filters, PostgreSQL Row-Level Security (RLS) policies, and automated integration tests that attempt cross-tenant IDOR access."

### Q13: "What is actually implemented versus simulated?"
- **Answer**: "Core inventory, permission mapping, risk engine, attack-path discovery, evidence logging, and what-if simulation are fully implemented. Provider revocation actions in demo mode are tagged as `SIMULATION ONLY` unless a live provider API credentials pair is configured."

### Q14: "How do you validate your risk formula isn't arbitrary?"
- **Answer**: "Our formula is validated against 5 mathematical properties (Strict Monotonicity, Hierarchy Ordering, Clamping, Missing Data Resilience, Stale Decay) and verified with automated test vectors (`VEC-LOW` through `VEC-CRIT`)."

### Q15: "Why should an organization trust your remediation recommendations?"
- **Answer**: "Because every recommendation includes a What-If Simulation showing exact before/after risk scores, affected data assets, and an immutable evidence audit trail."

---

*SIH Judge Defensibility Guide v1.0 — Approved Competition Strategy.*
