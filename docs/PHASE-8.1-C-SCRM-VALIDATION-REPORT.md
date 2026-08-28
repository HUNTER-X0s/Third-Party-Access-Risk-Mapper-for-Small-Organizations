# AccessGuard Phase 8.1: Final C-SCRM Model Accuracy & Supplier-Risk Validation Report

**Phase:** 8.1  
**Date:** 2026-08-14  
**Status:** COMPLETED & 100% VERIFIED  
**Framework Alignment:** NIST SP 1326 (Final, July 2026), NIST SP 800-161 Rev. 1, NIST SP 800-18 Rev. 2 (Final, June 2026)

---

## 1. Executive Summary

Phase 8.1 executed a focused validation and polish pass over AccessGuard's Cyber Supply Chain Risk Management (C-SCRM) and Supplier Risk Intelligence subsystem. All terminology was audited against final NIST guidance, explainability factor breakdowns were added, concentration rationale was clarified, RBAC and tenant isolation boundaries were verified, and full test suites passed.

---

## 2. Terminology & Model Architecture Audit

### A. Five-Component Due Diligence Alignment
In accordance with **NIST SP 1326 (Final, July 2026)**, the five due-diligence components are structured as follows:

> **Structural Note:**  
> "AccessGuard scores selected due-diligence evidence domains (FOCI, Provenance, Resilience, Foundational Cyber Practices) while modeling Supply Chain Tiers as a separate structural dimension across the access graph."

### B. Indicator Scoping & Honesty Labels
To prevent false claims of complete framework assessment:
- **Foundational Cyber Practices:** Formally labeled as **"SELECTED FOUNDATIONAL CYBER PRACTICE INDICATORS"** (MFA, Vulnerability Management, Incident Response Testing). Full NIST Foundational Cyber Practices coverage is not claimed.
- **Resilience:** Formally labeled as **"SELECTED RESILIENCE EVIDENCE"** (SLA %, BCP/DR documentation, Backup Recovery Testing). Full operational resilience assessment is not claimed.
- **FOCI:** Distinguishes `OBSERVED FACT`, `ASSESSED_NO_CONCERN`, `POTENTIAL_CONCERN`, and `UNKNOWN`. Incomplete country or ownership data is labeled `UNKNOWN`, never assumed to be an active concern.
- **Provenance:** Distinguishes `CLAIM` (supplier-provided declaration) from `ASSESSED` (observed evidence) and `UNKNOWN`.

---

## 3. Supplier Risk Explainability & Factor Breakdown

The `SupplierRiskEngine` now exposes `explain_supplier_risk(vendor_id)` (`GET /api/v1/vendors/{vendor_id}/explain`), decomposing supplier risk into deterministic, traceable contributors:
- **Business Criticality Contributor:** Flags core operational workflow reliance.
- **Crown Jewel Reachability:** Highlights direct access paths to level-5 sensitive assets.
- **Assessment Freshness:** Explicitly flags `OVERDUE` or `STALE` assessment status.
- **Resilience Gap:** Identifies missing backup recovery verifications or SLA gaps.
- **Cyber Practice Gap:** Highlights missing MFA enforcement or unverified incident response.
- **Provenance / FOCI Uncertainty:** Explains unverified hosting or foreign ownership structures.

---

## 4. Access Risk vs Supplier Risk Validation

| Scenario | Supplier Posture Risk | Technical Access Risk | Overall Priority | Validation Outcome |
|---|---|---|---|---|
| **Case A** (e.g. GitHub) | Low (20.0) | High (Crown Jewel read/admin) | **P0** (Immediate Action) | ✅ Favorable supplier assurance **never suppresses** elevated access risk. |
| **Case B** (e.g. AI Productivity Tool) | High (85.0) | Low / Shadow integration | **P0/P1** (Governance Review) | ✅ Supplier due diligence concern remains elevated and visible. |
| **Case C** (e.g. Zapier) | High (62.0) | High (Multi-SaaS sync) | **P0** (Immediate Action) | ✅ Compound exposure receives highest operational priority. |

---

## 5. Concentration & Single-Supplier Failure Simulation

- **Concentration Rationale:** `calculate_concentration_risk()` returns deterministic `concentration_reasons` explaining *why* concentration is elevated (e.g. reachability to Crown Jewels, multi-instance deployment, high percentage of tracked organizational data).
- **Failure Simulation Labeling:** Explicitly tagged with `simulation_label: "SIMULATION ONLY"` and `impact_nature: "POTENTIAL BUSINESS IMPACT"`. Reuses graph engine reachability logic without predicting real-world outages.

---

## 6. Assessment Versioning & Audit Trail

- Every modification to supplier due diligence:
  1. Increments `version` on `SupplierDueDiligence`.
  2. Appends an immutable snapshot to `SupplierAssessmentHistory`.
  3. Logs an `AuditEvent` with action `SUPPLIER_ASSESSMENT_UPDATED` and user attribution.
- Validated via `test_assessment_version_history_audit_trail`.

---

## 7. Role-Based Access Control & Tenant Isolation

| Role | View Suppliers & Explainability | Update Due Diligence Assessment |
|---|---|---|
| `VIEWER` | ✅ Permitted (200) | ❌ Denied (403 Forbidden) |
| `AUDITOR` | ✅ Permitted (200) | ❌ Denied (403 Forbidden) |
| `APP_OWNER` | ✅ Permitted (200) | ❌ Denied (403 Forbidden) |
| `DATA_OWNER` | ✅ Permitted (200) | ❌ Denied (403 Forbidden) |
| `IT_ADMIN` | ✅ Permitted (200) | ✅ Permitted (200) |
| `SECURITY_ADMIN` | ✅ Permitted (200) | ✅ Permitted (200) |
| `SUPER_ADMIN` | ✅ Permitted (200) | ✅ Permitted (200) |

Cross-tenant access across all vendor and supply chain graph endpoints is completely blocked via mandatory `organization_id` query filtering.

---

## 8. AI Supplier Analyst Guardrails

- **Capabilities:** Explains supplier risk factors, evidence anchors, concentration analysis, and NIST SP 1326 alignment.
- **Strict Invariants:**
  - Cannot calculate or modify risk scores.
  - Cannot update due diligence assessments or change supplier status.
  - Cannot approve or restrict vendors.
  - Cannot claim formal framework compliance or certification.
  - Prompt injection attacks through supplier notes are sanitized before bounded prompt injection.

---

## 9. Final Test Suite Results

- **Phase 8.1 Dedicated Tests:** 7 tests in `backend/tests/test_phase81_csrm_validation.py` (100% green).
- **All Phase 8 Tests:** 34 tests across 7 modules (100% green).
- **Full Project Regression:** **177 / 177 tests passing (100% green)** across 48 test modules.
- **Frontend Production Build:** Vite build succeeded with **0 errors** (1652 modules transformed).
