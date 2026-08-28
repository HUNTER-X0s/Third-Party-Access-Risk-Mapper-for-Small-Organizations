# 02 — Feature Matrix
# AccessGuard: Complete Feature Inventory & Classification

**Document Type:** Feature Matrix — Phase 0  
**Version:** 1.0  
**Date:** 2026-08-13  

---

## Tier Definitions

| Tier | Label | Description |
|---|---|---|
| **TIER 0** | Required by Problem Statement | Explicitly required; not optional |
| **TIER 1** | Required for Strong Submission | Implied by problem; expected by judges; strong competitive minimum |
| **TIER 2** | National-Level Differentiator | Elevates from "good" to "excellent"; creates competitive advantage |
| **TIER 3** | Future Commercial Roadmap | Valuable but out of hackathon scope; document architecture only |
| **EXCLUDE** | Out of Scope | Does not contribute to the product vision; excluded explicitly |

---

## Feature Analysis

### F-001 — Application Inventory

**Tier:** TIER 0  
**Why it matters:** Foundation of everything. Cannot assess risk without knowing what exists.  
**Problem statement relation:** Directly stated: "inventory authorized third-party applications"  
**Judge value:** HIGH — First thing any judge will look for  
**Technical complexity:** LOW–MEDIUM (CRUD + provider integration)  
**Demo value:** HIGH — Visible, tangible, immediately understandable  
**Security value:** HIGH — Visibility is the precondition for all other security actions  
**Implement:** YES — Must be fully working  
**Implementation scope:** Full implementation  

Fields: name, vendor, category, status (active/dormant/revoked), authorization date, authorized_by user, last_activity, scopes/permissions granted, provider type, OAuth client ID

---

### F-002 — Vendor Inventory

**Tier:** TIER 1  
**Why it matters:** An app is a product; the vendor is the supply chain entity. Multiple apps can belong to one vendor. Vendor risk aggregates across their apps.  
**Problem statement relation:** Implied ("external vendors")  
**Judge value:** HIGH — Shows supply-chain awareness  
**Technical complexity:** LOW  
**Demo value:** MEDIUM — Context for app risk  
**Security value:** HIGH — Vendor concentration risk is a real attack vector  
**Implement:** YES — Full implementation  
**Implementation scope:** Full implementation with risk aggregation  

Fields: name, website, SOC 2 status, privacy policy URL, country of incorporation, security contact, known incidents, aggregate risk score

---

### F-003 — Permission Inventory

**Tier:** TIER 0  
**Why it matters:** Permissions are the mechanism through which apps access data. Cannot do excess detection or risk scoring without a permission catalog.  
**Problem statement relation:** Directly stated: "map permissions"  
**Judge value:** HIGH  
**Technical complexity:** MEDIUM (normalization across providers is complex)  
**Demo value:** HIGH — Makes the invisible visible  
**Security value:** HIGH  
**Implement:** YES — Full implementation  

---

### F-004 — OAuth Scope Analysis

**Tier:** TIER 1  
**Why it matters:** Most modern third-party access uses OAuth 2.0. OAuth scopes are the permission mechanism. Understanding what each scope means in human terms is essential.  
**Problem statement relation:** Core to "map permissions"  
**Judge value:** HIGH — Shows technical depth in OAuth security (RFC 9700 awareness)  
**Technical complexity:** MEDIUM  
**Demo value:** HIGH  
**Security value:** HIGH  
**Implement:** YES — Build scope library with normalized human-readable descriptions  

---

### F-005 — Permission Normalization

**Tier:** TIER 2  
**Why it matters:** Google's `https://www.googleapis.com/auth/gmail.readonly` and Microsoft's `Mail.Read` are semantically equivalent but syntactically different. Normalization enables cross-provider comparison.  
**Problem statement relation:** Enables meaningful permission mapping  
**Judge value:** HIGH — Technical sophistication differentiator  
**Technical complexity:** HIGH — Requires semantic scope mapping per provider  
**Demo value:** MEDIUM  
**Security value:** HIGH  
**Implement:** YES (seed with Google + Microsoft normalization tables; architecture for extension)  

---

### F-006 — Least Privilege Analysis

**Tier:** TIER 0  
**Why it matters:** The central mechanism of excess permission detection. Compare what permissions an app HAS against what it NEEDS for its stated business purpose.  
**Problem statement relation:** Directly stated: "identify excessive access"  
**Judge value:** VERY HIGH — Core hackathon requirement  
**Technical complexity:** MEDIUM–HIGH (requires business purpose classification + permission-to-purpose mapping)  
**Demo value:** VERY HIGH — Clear, visual, compelling  
**Security value:** VERY HIGH  
**Implement:** YES — Full implementation  

---

### F-007 — Excess Permission Detection

**Tier:** TIER 0  
**Why it matters:** The output of least-privilege analysis. Surfaces specific permissions that are unnecessary.  
**Problem statement relation:** Directly stated: "identify excessive access"  
**Judge value:** VERY HIGH  
**Technical complexity:** MEDIUM  
**Demo value:** VERY HIGH  
**Security value:** VERY HIGH  
**Implement:** YES — Full implementation  

---

### F-008 — Data Classification

**Tier:** TIER 1  
**Why it matters:** Risk depends on what data is accessible. `read_all` access to a chat history is very different from `read_all` access to financial records. Classification is the foundation of data-level risk.  
**Problem statement relation:** Implied by "map permissions and data flows"  
**Judge value:** HIGH  
**Technical complexity:** MEDIUM  
**Demo value:** HIGH  
**Security value:** HIGH  
**Implement:** YES — Pre-defined classification taxonomy: PII, Financial, IP/Trade Secrets, Operational, Public  

---

### F-009 — Data Asset Inventory

**Tier:** TIER 1  
**Why it matters:** Organizations have named data assets (Customer Records, Financial Reports, Source Code, Email Archive). Mapping permissions to these assets makes risk concrete.  
**Problem statement relation:** Implied by "data flows"  
**Judge value:** HIGH  
**Technical complexity:** MEDIUM  
**Demo value:** HIGH — "Which apps can read your Customer Records?" is a powerful demo moment  
**Security value:** HIGH  
**Implement:** YES — Full implementation  

---

### F-010 — Data-Flow Visualization

**Tier:** TIER 0  
**Why it matters:** The primary visual output of the system. Makes permission-data relationships intuitive.  
**Problem statement relation:** Directly stated: "data-flow visualization"  
**Judge value:** VERY HIGH — Visual impact during demo  
**Technical complexity:** MEDIUM–HIGH (React Flow graph engine)  
**Demo value:** VERY HIGH  
**Security value:** HIGH (communication tool)  
**Implement:** YES — Interactive graph with filtering, highlighting, risk overlays  

---

### F-011 — Risk Scoring

**Tier:** TIER 0  
**Why it matters:** Converts visibility into priority. Without scoring, the user faces a list they cannot prioritize.  
**Problem statement relation:** Directly stated: "risk scoring"  
**Judge value:** VERY HIGH  
**Technical complexity:** MEDIUM–HIGH (multi-factor deterministic engine)  
**Demo value:** HIGH  
**Security value:** VERY HIGH  
**Implement:** YES — Full deterministic engine  

---

### F-012 — Explainable Risk Scoring

**Tier:** TIER 2  
**Why it matters:** Black-box scores are untrustworthy. Explainability makes the system credible, auditable, and educational.  
**Problem statement relation:** Implied (audit-quality output)  
**Judge value:** VERY HIGH — Key differentiator; shows technical maturity  
**Technical complexity:** MEDIUM  
**Demo value:** VERY HIGH  
**Security value:** HIGH  
**Implement:** YES — Every score must show contributing factors with weights  

---

### F-013 — Business Impact Scoring

**Tier:** TIER 2  
**Why it matters:** Technical risk severity alone doesn't tell a business owner what to do. Business impact (revenue, reputation, regulatory) bridges the gap.  
**Problem statement relation:** Implied (remediation prioritization)  
**Judge value:** HIGH  
**Technical complexity:** MEDIUM  
**Demo value:** HIGH  
**Security value:** HIGH  
**Implement:** YES — Integrate into risk score as a weighted factor  

---

### F-014 — Vendor Risk

**Tier:** TIER 1  
**Why it matters:** An app's risk depends partly on who built it. A vendor with a known security incident history is higher risk regardless of current permissions.  
**Problem statement relation:** Implied ("external vendors")  
**Judge value:** HIGH  
**Technical complexity:** MEDIUM  
**Demo value:** MEDIUM  
**Security value:** HIGH  
**Implement:** YES — Vendor trust score as factor in app risk  

---

### F-015 — Supply Chain Risk

**Tier:** TIER 1  
**Why it matters:** The app you authorized may itself use other third-party services. This creates chain risk (third-party to fourth-party).  
**Problem statement relation:** Implied ("external vendors")  
**Judge value:** HIGH — Shows sophisticated understanding of supply-chain concepts  
**Technical complexity:** MEDIUM  
**Demo value:** MEDIUM  
**Security value:** HIGH  
**Implement:** YES — Surface in vendor profile; document as supply-chain depth  

---

### F-016 — Fourth-Party Risk

**Tier:** TIER 3  
**Why it matters:** Vendors' vendors. Risk propagates through supply chains.  
**Implement:** ARCHITECTURE ONLY — Document concept; no implementation in hackathon  

---

### F-017 — Shadow SaaS Detection

**Tier:** TIER 2  
**Why it matters:** Apps authorized by users without IT knowledge are the highest-risk category.  
**Problem statement relation:** Implied (identifying all authorized apps, not just IT-approved)  
**Judge value:** HIGH  
**Technical complexity:** MEDIUM  
**Demo value:** HIGH — "We found 12 apps you didn't know about" is a powerful moment  
**Security value:** VERY HIGH  
**Implement:** YES — Flag apps not in the approved list; distinguish approved vs. discovered  

---

### F-018 — Permission-Change Detection

**Tier:** TIER 1  
**Why it matters:** An app that quietly expands its permissions is a major risk indicator.  
**Problem statement relation:** Implied (continuous monitoring)  
**Judge value:** HIGH  
**Technical complexity:** MEDIUM  
**Demo value:** HIGH  
**Security value:** VERY HIGH  
**Implement:** YES — Permission delta tracking and alerting  

---

### F-019 — Security Event Timeline

**Tier:** TIER 1  
**Why it matters:** Chronological view of all permission changes, reviews, and anomalies.  
**Problem statement relation:** Audit context  
**Judge value:** MEDIUM–HIGH  
**Technical complexity:** LOW–MEDIUM  
**Demo value:** HIGH — Shows organizational history  
**Security value:** HIGH  
**Implement:** YES  

---

### F-020 — Behavioral Anomaly Detection

**Tier:** TIER 3  
**Why it matters:** Statistical detection of unusual access patterns.  
**Technical complexity:** VERY HIGH (requires baseline data + ML)  
**Implement:** ARCHITECTURE ONLY — Roadmap item  

---

### F-021 — Attack Path Analysis

**Tier:** TIER 2  
**Why it matters:** Shows how a compromised app could reach critical data assets through chained permissions and relationships. Elevates from "what can this app do" to "what could an attacker do if they owned this app."  
**Problem statement relation:** Implied by "risk map" + excess detection  
**Judge value:** VERY HIGH — Strongest technical differentiator  
**Technical complexity:** HIGH  
**Demo value:** VERY HIGH  
**Security value:** VERY HIGH  
**Implement:** YES — Graph traversal with realistic attack path scenarios  

---

### F-022 — Blast-Radius Analysis

**Tier:** TIER 2  
**Why it matters:** Calculates total reachable data assets if a specific app is compromised.  
**Problem statement relation:** Enhances remediation prioritization  
**Judge value:** VERY HIGH  
**Technical complexity:** HIGH  
**Demo value:** VERY HIGH — "If Zapier is compromised, these 8 data assets are exposed"  
**Security value:** VERY HIGH  
**Implement:** YES — Tied to attack path graph; show total exposed assets  

---

### F-023 — Risk Heatmaps

**Tier:** TIER 1  
**Why it matters:** Visual representation of risk distribution across the application landscape.  
**Judge value:** HIGH  
**Technical complexity:** LOW–MEDIUM  
**Demo value:** HIGH  
**Implement:** YES — Risk heatmap in dashboard  

---

### F-024 — Risk Aging

**Tier:** TIER 1  
**Why it matters:** A high-risk finding that has been open for 90 days is worse than one that opened yesterday.  
**Implement:** YES — Age risk findings; increase severity over time without action  

---

### F-025 — Risk SLA

**Tier:** TIER 2  
**Why it matters:** Organizationally defined deadlines for addressing risk findings.  
**Implement:** PARTIAL — Basic SLA concept with overdue flagging  

---

### F-026 — Policy Engine

**Tier:** TIER 2  
**Why it matters:** Allows organizations to define their own rules ("No app may have admin-level access without review").  
**Technical complexity:** HIGH  
**Implement:** YES — Simple rule-based policy engine (5–10 predefined policies + custom rule UI)  

---

### F-027 — Policy-as-Code

**Tier:** TIER 3  
**Why it matters:** Machine-readable policy definitions for CI/CD integration.  
**Implement:** ARCHITECTURE ONLY  

---

### F-028 — Remediation Recommendations

**Tier:** TIER 0  
**Why it matters:** Directly stated by problem statement. Prioritized, actionable steps.  
**Implement:** YES — Full implementation with step-by-step actions, expected risk reduction  

---

### F-029 — What-If Remediation Simulation

**Tier:** TIER 2  
**Why it matters:** Shows risk impact BEFORE taking action. "If you revoke these 3 scopes, risk drops from 85 to 42."  
**Judge value:** VERY HIGH — Unique and powerful differentiator  
**Technical complexity:** MEDIUM (recalculate risk score with proposed changes)  
**Demo value:** VERY HIGH  
**Implement:** YES — Simulation mode in remediation UI  

---

### F-030 — Approval Workflows

**Tier:** TIER 2  
**Why it matters:** Multi-person review and approval before remediation actions.  
**Technical complexity:** MEDIUM  
**Implement:** PARTIAL — Basic approval concept; full workflow in roadmap  

---

### F-031 — Security Posture Score

**Tier:** TIER 1  
**Why it matters:** Organization-wide single number summarizing overall access risk health.  
**Implement:** YES — Derived from aggregate of all app risk scores  

---

### F-032 — Compliance Mapping

**Tier:** TIER 2  
**Why it matters:** Maps findings to relevant compliance frameworks (SOC 2, ISO 27001).  
**Implement:** PARTIAL — Reference mapping table; no formal compliance claim  

---

### F-033 — Audit Evidence

**Tier:** TIER 1  
**Why it matters:** Structured evidence of access reviews and findings for external auditors.  
**Implement:** YES — Evidence export tied to audit report  

---

### F-034 — Audit Trails

**Tier:** TIER 1  
**Why it matters:** Immutable log of all system actions.  
**Implement:** YES — Append-only audit log  

---

### F-035 — Report Generation

**Tier:** TIER 0  
**Why it matters:** Directly stated. Multiple report types (executive, technical, audit).  
**Implement:** YES — PDF + JSON export  

---

### F-036 — AI Security Analyst

**Tier:** TIER 2  
**Why it matters:** Natural language Q&A ("What is my biggest risk right now?") makes the system accessible to non-technical users.  
**Judge value:** HIGH — Modern, compelling  
**Technical complexity:** MEDIUM (LLM integration with context injection)  
**Security constraints:** Advisory only; cannot modify data or override risk scores  
**Implement:** YES — Advisory AI layer with clear "AI Suggestion" labeling  

---

### F-037 — Natural Language Querying

**Tier:** TIER 2  
**Why it matters:** "Show me all apps with email read access" in plain English.  
**Implement:** YES — Thin layer over AI analyst  

---

### F-038 — Scenario Simulation

**Tier:** TIER 3  
**Why it matters:** "What if we added this app?" simulation.  
**Implement:** ARCHITECTURE ONLY  

---

### F-039 — Integration Framework / Connector Framework

**Tier:** TIER 1 (architecture); TIER 3 (full implementation)  
**Why it matters:** Real data is more compelling than demo data.  
**Implement:** Architecture implemented; 1–2 real connectors as proof-of-concept (Google Workspace priority)  

---

### F-040 — Multi-Tenancy

**Tier:** TIER 1  
**Why it matters:** Multiple organizations using the platform. Critical for production readiness.  
**Implement:** YES — Multi-tenant from day one  

---

### F-041 — RBAC

**Tier:** TIER 1  
**Why it matters:** Different roles (admin, analyst, viewer) with different permissions.  
**Implement:** YES — 3–4 roles minimum  

---

### F-042 — Security Monitoring (of AccessGuard itself)

**Tier:** TIER 1  
**Why it matters:** The security platform must itself be monitored.  
**Implement:** YES — Audit log + alerting on anomalous access to the platform  

---

### F-043 — Security Posture History

**Tier:** TIER 1  
**Why it matters:** Trend line — are we getting better or worse over time?  
**Implement:** YES — Store historical posture scores; render trend chart  

---

## Feature Decision Summary

| ID | Feature | Tier | Implement? |
|---|---|---|---|
| F-001 | Application Inventory | 0 | ✅ Full |
| F-002 | Vendor Inventory | 1 | ✅ Full |
| F-003 | Permission Inventory | 0 | ✅ Full |
| F-004 | OAuth Scope Analysis | 1 | ✅ Full |
| F-005 | Permission Normalization | 2 | ✅ Seed data |
| F-006 | Least Privilege Analysis | 0 | ✅ Full |
| F-007 | Excess Permission Detection | 0 | ✅ Full |
| F-008 | Data Classification | 1 | ✅ Full |
| F-009 | Data Asset Inventory | 1 | ✅ Full |
| F-010 | Data-Flow Visualization | 0 | ✅ Full |
| F-011 | Risk Scoring | 0 | ✅ Full |
| F-012 | Explainable Risk Scoring | 2 | ✅ Full |
| F-013 | Business Impact Scoring | 2 | ✅ Full |
| F-014 | Vendor Risk | 1 | ✅ Full |
| F-015 | Supply Chain Risk | 1 | ✅ Conceptual |
| F-016 | Fourth-Party Risk | 3 | 🗺 Roadmap only |
| F-017 | Shadow SaaS Detection | 2 | ✅ Full |
| F-018 | Permission-Change Detection | 1 | ✅ Full |
| F-019 | Security Event Timeline | 1 | ✅ Full |
| F-020 | Behavioral Anomaly Detection | 3 | 🗺 Roadmap only |
| F-021 | Attack Path Analysis | 2 | ✅ Full |
| F-022 | Blast-Radius Analysis | 2 | ✅ Full |
| F-023 | Risk Heatmaps | 1 | ✅ Full |
| F-024 | Risk Aging | 1 | ✅ Full |
| F-025 | Risk SLA | 2 | ⚡ Partial |
| F-026 | Policy Engine | 2 | ✅ Simplified |
| F-027 | Policy-as-Code | 3 | 🗺 Roadmap only |
| F-028 | Remediation Recommendations | 0 | ✅ Full |
| F-029 | What-If Simulation | 2 | ✅ Full |
| F-030 | Approval Workflows | 2 | ⚡ Partial |
| F-031 | Security Posture Score | 1 | ✅ Full |
| F-032 | Compliance Mapping | 2 | ⚡ Reference only |
| F-033 | Audit Evidence | 1 | ✅ Full |
| F-034 | Audit Trails | 1 | ✅ Full |
| F-035 | Report Generation | 0 | ✅ Full |
| F-036 | AI Security Analyst | 2 | ✅ Advisory |
| F-037 | Natural Language Querying | 2 | ✅ Via AI |
| F-038 | Scenario Simulation | 3 | 🗺 Roadmap only |
| F-039 | Integration Framework | 1/3 | ⚡ Arch + 1 connector |
| F-040 | Multi-Tenancy | 1 | ✅ Full |
| F-041 | RBAC | 1 | ✅ Full |
| F-042 | Platform Security Monitoring | 1 | ✅ Full |
| F-043 | Security Posture History | 1 | ✅ Full |

**Legend:** ✅ Full implementation | ⚡ Partial implementation | 🗺 Roadmap/architecture only

---

*Feature matrix version 1.0 — Subject to revision during implementation planning.*
