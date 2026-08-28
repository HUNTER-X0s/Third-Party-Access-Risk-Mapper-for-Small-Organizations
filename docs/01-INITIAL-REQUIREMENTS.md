# 01 — Initial Requirements
# AccessGuard: Comprehensive Requirements Discovery

**Document Type:** Requirements Discovery — Phase 0  
**Version:** 1.0  
**Date:** 2026-08-13  

---

## Overview

This document captures requirements discovered through multi-stakeholder perspective analysis. Requirements are classified by type and origin (explicit vs. inferred). The goal is to ensure the implementation scope covers everything a national-level hackathon judge would expect — including implicit and unstated requirements.

---

## Part A — Stakeholder Perspective Analysis

### Perspective 1: Small Business Owner

**Context:** 15-person marketing agency. Uses Google Workspace, Slack, HubSpot, Zapier, Dropbox, Notion, and 7 other integrations. No dedicated IT staff.

**Core Concerns:**
- "I don't know which apps have access to what — I just click 'allow' when they ask"
- "What happens if one of these apps gets hacked?"
- "A former employee set up several integrations — I don't know what they authorized"
- "Can I get a simple report that tells me what to fix first?"

**Requirements Derived:**
- Must work for non-technical users (plain-language explanations)
- Must provide a simple prioritized action list ("Fix these 3 things today")
- Must identify orphaned authorizations (created by departed users)
- Must explain risk in business terms, not technical terms
- Must have a meaningful executive dashboard accessible in < 60 seconds

---

### Perspective 2: IT Administrator

**Context:** Single IT person for a 50-person organization. Manages Google Workspace, GitHub, Jira, Confluence, AWS, and multiple SaaS tools.

**Core Concerns:**
- "I need to know every app that's been authorized — including ones I didn't authorize myself"
- "Some integrations were set up years ago and I don't know if they're still needed"
- "I need to prove to the owner that we've reviewed our access controls"
- "I need to revoke something quickly when an employee leaves"

**Requirements Derived:**
- Must show all authorized applications, not just IT-approved ones
- Must show authorization date and authorizing user
- Must support access review workflows (review + approve or revoke)
- Must show last-activity date to identify stale/dormant applications
- Must generate audit evidence of completed reviews
- Must support fast revocation with clear remediation steps

---

### Perspective 3: Security Administrator

**Context:** Part-time security role at 100-person fintech company. Has security knowledge but limited resources.

**Core Concerns:**
- "I need to understand the real risk of each integration, not just a list of permissions"
- "Which app creates the biggest blast radius if compromised?"
- "I need to identify permission combinations that create elevated risk"
- "I need to map permissions to actual data types — 'read_files' tells me nothing unless I know what files"

**Requirements Derived:**
- Risk scoring must be multi-factor and explainable
- Must show permission-to-data-asset mapping
- Must support blast-radius analysis
- Must identify toxic permission combinations
- Must show attack-path reasoning
- Risk must correlate with business impact, not just technical severity
- Must detect excess permissions compared to stated business purpose

---

### Perspective 4: Application Owner

**Context:** Owns the marketing analytics platform. Has granted several integrations access to campaign data.

**Core Concerns:**
- "I need to know exactly what data each integration can see"
- "I need to validate that the access each integration has matches its stated purpose"
- "I should be notified if an integration's permissions change"

**Requirements Derived:**
- Permission-to-data mapping must be granular and accurate
- System must support business purpose declaration for each integration
- Must alert on permission changes for owned applications
- Must show historical permission state ("when did this app get email read access?")

---

### Perspective 5: Data Owner

**Context:** CFO who is the data owner for financial records stored in Google Drive and QuickBooks.

**Core Concerns:**
- "Which apps can read our financial spreadsheets?"
- "Has anything changed since last quarter?"
- "What data would be exposed if our Zapier account was compromised?"

**Requirements Derived:**
- Data asset inventory must exist (not just app inventory)
- Must show which apps have access to each data asset category
- Must support data asset classification (PII, Financial, IP, etc.)
- Must generate data-centric access reports ("who can read Financial data?")
- Must detect changes in data access from period to period

---

### Perspective 6: Auditor

**Context:** External auditor reviewing controls for SOC 2 readiness.

**Core Concerns:**
- "I need evidence that the organization reviews third-party access periodically"
- "I need to see who authorized each integration and when"
- "I need to understand what data each integration can access"
- "I need to see that excessive permissions are detected and acted upon"

**Requirements Derived:**
- Complete authorization audit trail (who, what, when, why)
- Access review workflow with documented outcomes
- Evidence export in standard format (PDF, JSON)
- Historical state preservation (point-in-time access snapshots)
- Policy violation documentation
- Remediation action log with timestamps
- Report generation with auditor-facing structure

---

### Perspective 7: CISO / Security Lead

**Context:** Part-time CISO at a 200-person organization. Reports to board quarterly.

**Core Concerns:**
- "I need a security posture score I can present to the board"
- "I need trend data — are we getting better or worse?"
- "I need to understand our top 5 third-party risks"
- "I need to identify which vendors have highest aggregate risk"

**Requirements Derived:**
- Organization-level security posture score (0–100)
- Trend visualization over time
- Top-N risk items surfaced prominently
- Vendor-level risk aggregation
- Executive summary report (non-technical language)
- Risk reduction tracking (before/after remediation)

---

### Perspective 8: Government Evaluator / Hackathon Judge

**Context:** Evaluating national cybersecurity competition submissions. Experienced in both policy and technical domains.

**Core Concerns:**
- "Does this solve a real, significant problem?"
- "Is the security model credible?"
- "Is the risk scoring defensible and explainable?"
- "Does this show genuine technical depth beyond a basic CRUD application?"
- "Would this actually help a small organization improve its security posture?"
- "Are claims supported by the actual system?"

**Requirements Derived (Implicit):**
- Must demonstrate a coherent security model, not just a feature list
- Risk engine must be deterministic, transparent, and defensible
- Must show genuine understanding of OAuth, permissions, and access governance
- Must demonstrate awareness of attack surface and threat modeling
- Must not claim compliance or certification without evidence
- Must have a compelling, clear 3-minute demo path
- Must show concrete, quantifiable value ("reduces risk by X%")
- Standards references must be accurate and appropriate

---

### Perspective 9: Security Researcher

**Core Concerns:**
- "Is the underlying security model sound?"
- "Are the attack paths realistic?"
- "Is the permission model accurate?"
- "Are there architectural security weaknesses in the platform itself?"

**Requirements Derived:**
- Security model must be documented and defensible
- Platform security must follow industry best practices (OWASP, NIST)
- No security theater — every claim must be technically grounded
- Attack path modeling must follow realistic threat scenarios

---

### Perspective 10: Vendor Manager

**Core Concerns:**
- "Which vendors have the most access to our systems?"
- "Which vendors have had security incidents?"
- "Can I see a vendor's risk posture in one view?"

**Requirements Derived:**
- Vendor inventory separate from (but linked to) application inventory
- Vendor-level risk aggregation across all their applications
- Vendor security metadata (certifications, incident history if known)
- Vendor concentration risk (single vendor controlling too many critical integrations)

---

## Part B — Classified Requirements

### B1. Explicit Requirements (from Problem Statement)

| ID | Requirement | Source |
|---|---|---|
| EX-01 | Inventory authorized third-party applications | Problem Statement |
| EX-02 | Map permissions for each application | Problem Statement |
| EX-03 | Visualize data flows | Problem Statement |
| EX-04 | Score risk for each application/permission | Problem Statement |
| EX-05 | Detect excess permissions | Problem Statement |
| EX-06 | Produce remediation recommendations | Problem Statement |
| EX-07 | Generate audit reports | Problem Statement |
| EX-08 | Produce a visual risk map | Expected Outcome |

### B2. Implicit Requirements (reasonably expected)

| ID | Requirement | Derived From |
|---|---|---|
| IM-01 | Explain risk scores in human-readable terms | Non-technical primary users |
| IM-02 | Support multi-user access with roles | Organization context |
| IM-03 | Track authorization history (who, when) | Audit needs |
| IM-04 | Identify stale/dormant application authorizations | Security best practice |
| IM-05 | Map permissions to specific data asset types | Real-world risk assessment |
| IM-06 | Show vendor-level risk aggregation | TPRM context |
| IM-07 | Support business purpose declaration | Least-privilege validation |
| IM-08 | Detect permission changes over time | Change management |
| IM-09 | Provide trend data (improving / degrading) | CISO reporting needs |
| IM-10 | Support demo mode with high-quality seeded data | Hackathon context |

### B3. Security Requirements

| ID | Requirement |
|---|---|
| SEC-01 | All authentication via secure mechanisms (JWT + PKCE OAuth 2.0) |
| SEC-02 | Server-side authorization on every API endpoint |
| SEC-03 | Strict tenant isolation in all data queries |
| SEC-04 | All external data treated as untrusted and validated |
| SEC-05 | No hardcoded secrets in codebase |
| SEC-06 | Complete audit trail of all user actions |
| SEC-07 | Input validation and output encoding to prevent XSS/injection |
| SEC-08 | Rate limiting on all API endpoints |
| SEC-09 | Encrypted sensitive fields at rest |
| SEC-10 | CSRF protection on all state-changing endpoints |
| SEC-11 | AI layer isolated from security-critical code paths |
| SEC-12 | Risk engine is deterministic and AI-independent |

### B4. Business Requirements

| ID | Requirement |
|---|---|
| BUS-01 | Accessible to non-technical business owners |
| BUS-02 | Risk expressed in business impact terms |
| BUS-03 | Actionable remediation (specific, prioritized steps) |
| BUS-04 | Report format suitable for leadership presentation |
| BUS-05 | Demonstrates measurable risk reduction |
| BUS-06 | Low barrier to entry (no security expertise required) |
| BUS-07 | Quick time-to-value (meaningful insight within minutes of setup) |

### B5. Usability Requirements

| ID | Requirement |
|---|---|
| UX-01 | Primary dashboard actionable within 10 seconds of viewing |
| UX-02 | Risk scores accompanied by plain-language explanations |
| UX-03 | Navigation intuitive for non-security users |
| UX-04 | Visual risk map comprehensible without training |
| UX-05 | Mobile-responsive for executives reviewing on mobile |
| UX-06 | Loading states and feedback for all async operations |
| UX-07 | Empty states with guidance (not just blank screens) |

### B6. Audit Requirements

| ID | Requirement |
|---|---|
| AUD-01 | Complete history of authorization changes |
| AUD-02 | Timestamped record of all access reviews |
| AUD-03 | Evidence export in PDF and structured format |
| AUD-04 | Policy violation log with resolution tracking |
| AUD-05 | Audit trail immutability (append-only log) |
| AUD-06 | Point-in-time access state reconstruction |

### B7. Scalability Requirements

| ID | Requirement |
|---|---|
| SCA-01 | Architecture supports eventual migration to services |
| SCA-02 | Database schema designed for multi-tenancy from day one |
| SCA-03 | Background job queue for async processing |
| SCA-04 | Connector framework designed for provider extensibility |
| SCA-05 | Risk engine isolated as internal service boundary |

### B8. Privacy Requirements

| ID | Requirement |
|---|---|
| PRI-01 | Minimal collection of personal data |
| PRI-02 | User data scoped to their organization only |
| PRI-03 | No cross-tenant user data exposure |
| PRI-04 | Audit logs exclude sensitive PII where possible |
| PRI-05 | Data retention policy configurable per organization |

### B9. Reliability Requirements

| ID | Requirement |
|---|---|
| REL-01 | Core inventory and risk views work without external API connection |
| REL-02 | AI layer failure does not break core functionality |
| REL-03 | Risk scores computable from stored data (no live recalculation required every time) |
| REL-04 | Graceful degradation when connectors are unavailable |

### B10. Explainability Requirements

| ID | Requirement |
|---|---|
| EXP-01 | Every risk score must show contributing factors |
| EXP-02 | Each factor must be individually visible and understandable |
| EXP-03 | Risk scores must be reproducible from the same inputs |
| EXP-04 | Remediation recommendations must explain expected risk reduction |
| EXP-05 | Attack paths must be navigable (show each hop) |
| EXP-06 | AI explanations must be clearly labeled as AI-generated |

---

## Part C — What National Judges Will Likely Expect

Even if not explicitly written, judges at a national cybersecurity hackathon will likely evaluate against:

1. **Technical depth of the security model** — Is the risk model defensible, or is it superficial?
2. **Standards awareness** — Does the team understand NIST, OWASP, CISA, and how they apply?
3. **Real-world applicability** — Would this actually help a real small organization?
4. **Security of the platform itself** — Does the security tool follow its own principles?
5. **Non-black-box risk scoring** — Can you explain WHY something is high risk?
6. **Attack surface understanding** — Do you understand how permissions translate to real threats?
7. **Innovation vs. copycat** — Is there a genuine differentiating insight?
8. **Demo quality** — Is the demo polished, clear, and compelling?
9. **Scope realism** — Is the team honest about what is and isn't implemented?
10. **Business impact** — Can you quantify what risk reduction looks like in dollars or incidents?

---

*Document version 1.0 — Requirements discovery complete for Phase 0.*
