# PHASE-0.5 ARCHITECTURE REVIEW & HARDENING REPORT
# AccessGuard: Adversarial & Quality Assessment of Phase 0 Blueprint

**Document Type:** Architecture Review & Hardening  
**Version:** 0.5  
**Date:** 2026-08-13  
**Status:** Approved Specification  

---

## 1. Executive Summary

Phase 0 established a strong conceptual foundation for AccessGuard. However, a rigorous review from the perspectives of a **Principal Security Architect, CISO, Staff Full-Stack Engineer, Product Design Lead, Application Security Red-Teamer, and Smart India Hackathon (SIH) Jury Member** revealed critical architectural, security, and product-design gaps that would compromise credibility during national competition or real-world deployment.

### Critical Gaps Identified in Phase 0:

1. **AI Dashboard Aesthetics Risk**: Phase 0 assumed standard `shadcn/ui` components without defining a strict operational design system, risking a generic "AI-generated hackathon template" look.
2. **Missing Evidence & Provenance**: Findings lacked explicit immutable evidence linkages (`SOURCE -> OBSERVATION -> NORMALIZATION -> RULE -> FINDING`), making scores seem arbitrary to auditors/judges.
3. **Over-Simplified Business Purpose Model**: Unstructured or unverified free-text business purpose declarations could be exploited to bypass least-privilege checks.
4. **Single Risk Number Collapse**: Collapsing all security logic into a single 0–100 score masked vital multi-dimensional nuances (Technical vs. Data Exposure vs. Business Impact vs. Vendor Risk).
5. **Graph Presentation vs. Reasoning**: React Flow was treated as the engine rather than a rendering layer over a mathematically rigorous directed graph domain model.
6. **Incomplete Finding Lifecycle**: Remediations lacked state-machine rigor (`NEW` to `VERIFIED` / `CLOSED`) and failed to distinguish simulated remediations from real API actions.
7. **Prompt Injection & Third-Party Metadata Trust**: External OAuth metadata was not explicitly isolated from AI context windows.

This document records the architectural hardening steps taken to resolve every single gap.

---

## 2. Multi-Role Peer Review Findings

### 2.1 Principal Security Architect Review
- **Critique**: "A single composite score is inadequate for security governance. A low vendor trust score shouldn't dilute a critical direct data exposure. Furthermore, findings must be backed by evidence records, not just database flags."
- **Hardening Action**: Separated risk into 5 distinct risk dimensions (Technical, Data Exposure, Business Impact, Vendor, Attack Path). Introduced a formal `Evidence` & `Provenance` domain model.

### 2.2 CISO Review
- **Critique**: "Small business owners need actionable priority, but auditors need proof. If AccessGuard says Zapier has excessive permissions, where is the proof of what it actually requested vs what the business process requires?"
- **Hardening Action**: Implemented a structured `BusinessPurpose` matrix with explicit `RequiredPermission` maps. Added PDF/JSON Evidence Packages with cryptographic verification hashes.

### 2.3 Staff Full-Stack Engineer Review
- **Critique**: "React Flow cannot be the source of truth for graph algorithms. We need an in-memory network graph layer in Python (e.g., NetworkX or adjacency list) that handles attack-path traversal and blast-radius calculations, with React Flow strictly handling node rendering."
- **Hardening Action**: Decoupled Graph Domain Model from Frontend rendering layer. Defined pure Python graph algorithms for BFS/DFS attack-path calculation and blast-radius set intersection.

### 2.4 Product Design Lead Review
- **Critique**: "The UI must look like Cloudflare, Wiz, or CrowdStrike—compact, operational, quiet, and data-dense. Zero floating blobs, zero purple AI gradients, zero card-in-card nesting."
- **Hardening Action**: Formulated `PRODUCT-DESIGN-SYSTEM.md` establishing a high-density, dark/light slate operational palette, strict monospaced data alignment, and split-pane investigation drawers.

### 2.5 AppSec / Red-Team Review
- **Critique**: "OAuth application titles like `<script>alert(1)</script>` or malicious OAuth scope descriptions could trigger XSS in the dashboard or prompt injection in Gemini."
- **Hardening Action**: Added mandatory strict Pydantic input sanitization, DOMPurify output encoding, Content Security Policy rules, and a Prompt Injection Defense pipeline (`UNTRUSTED -> SANITIZE -> BOUNDED CONTEXT -> LLM`).

### 2.6 SIH Jury Review
- **Critique**: "Judges reject projects that look like polished pitch decks with fake backends. We will ask: 'Show me the formula version, show me the raw OAuth response, show me what happens if the sync fails.'"
- **Hardening Action**: Created `SIH-JUDGE-DEFENSIBILITY.md` addressing all 15 adversarial judge questions, explicit `risk_engine_version` stamp on every finding, and system health status indicators (data freshness, sync status).

---

## 3. Key Architecture & Hardening Decisions

| Area | Phase 0 State | Phase 0.5 Hardened State |
|---|---|---|
| **Design Language** | Standard `shadcn/ui` defaults | Custom SecOps Design System (compact tables, split-pane drawers, high density, anti-AI visual rules) |
| **Evidence Model** | Database flag on grant | Immutable `Evidence` entity linked to raw observation, scope mapping, and collection timestamp |
| **Risk Scoring** | Single 0–100 score | 5 Dimensional Scores + Weighted Aggregation + Calibration & Monotonicity validation |
| **Business Purpose** | Free-text string | Structured Catalog + Mandatory Permission Mapping + Admin Approval workflow |
| **Graph Model** | React Flow component state | Server-side Graph Reasoning Engine (Adjacency Matrix / Network Traversal) + React Flow presentation |
| **Remediation** | Simple status toggle | 8-State Formal Lifecycle (`NEW` -> `CLOSED`) + explicit "SIMULATION ONLY" tag |
| **AI Layer** | Direct text prompt context | Bounded, Sanitized Context Pipeline with strict anti-injection boundary |
| **Demo Mode** | Basic seeded SQLite data | First-class `DEMO / SIMULATED ENVIRONMENT` with internally consistent multi-tier attack story |

---

## 4. Verification & Hardening Plan

1. **Data Model Validation**: All 25 original domain entities updated and 5 new entities (`Evidence`, `EvidenceSource`, `RiskDimension`, `RiskCalibrationVector`, `DataState`) integrated.
2. **Deterministic Risk Calibration**: Test vectors defined for Monotonicity, Boundary Behavior, and Missing Data resilience.
3. **Security Constraints**: `AGENTS.md` updated with strict permanent anti-AI design guidelines and evidence provenance enforcement.

*Phase 0.5 Architecture Review Complete.*
