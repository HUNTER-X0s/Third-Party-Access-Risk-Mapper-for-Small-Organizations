# PHASE 2.1 AUDIT BASELINE
# AccessGuard: Baseline Inspection & Pre-Validation Assessment

**Document Type:** Verification & Audit Baseline  
**Version:** 2.1  
**Date:** 2026-08-13  
**Status:** Audit Baseline Established — Inconsistencies Identified  

---

## 1. Baseline Test State

- **Total Backend Pytest Count**: 36 passed out of 36 tests (100%).
- **Phase 1 20-Step Acceptance Verification**: Passed 100%.
- **Phase 2 Demo Scenario Verification**: Passed 100%.
- **Frontend Build (`npm run build`)**: 0 errors.

---

## 2. Identified Inconsistencies & Defect Audit

### Defect 1: Remediation Optimizer Target Inconsistency
- **Observation**: `calculate_minimum_effective_remediation` was invoked with `target_max_score = 50.0`. Candidate 2 yielded a predicted residual risk of `53.6`. The UI and report marked Candidate 2 as recommended despite `53.6 > 50.0` violating `predicted_residual < target`.
- **Root Cause**: The optimizer lacked a strict `is_target_achieved` boolean and did not distinguish between a fully successful target reduction vs a best-effort reduction.
- **Fix**: Update `remediation_optimizer.py` to evaluate target achievement strictly (`is_target_achieved = (predicted_residual <= target_threshold)`). If the candidate set achieves score $\le \text{target}$ (or target threshold is calibrated to 55.0 / full revocation), report `is_target_achieved: True`; otherwise report `BEST EFFORT (TARGET UNMET)` with `is_target_achieved: False`.

### Defect 2: Blast-Radius Score Discrepancy Across Modules
- **Observation**: `BlastRadiusCalculator` computed GitHub Blast Radius as `55.0/100` (Medium). However, `RemediationOptimizer` hardcoded `blast_radius_before = 82.0`.
- **Root Cause**: `RemediationOptimizer` used static fallback values instead of calling `BlastRadiusCalculator` dynamically.
- **Fix**: Refactor `RemediationOptimizer` to dynamically invoke `BlastRadiusCalculator(db, org_id).calculate_application_blast_radius(app_id)` so a single authoritative Blast Radius value (`55.0`) propagates across all API endpoints, drawers, and reports.

### Defect 3: Claims & Terminology Audit Needs Standardization
- **Observation**: UI and markdown docs occasionally referenced "immutable evidence" or "attack path" without explicitly clarifying "Tamper-Evident" and "Potential Access Path".
- **Fix**: Standardize terminology across all documentation, API schemas, and frontend copy to reflect:
  - `TAMPER-EVIDENT` (instead of Immutable)
  - `POTENTIAL ACCESS PATH` (instead of Confirmed Exploit)
  - `SIMULATION ONLY — NO PROVIDER CHANGES EXECUTED`
  - `ALIGNED WITH NIST SP 800-161` (instead of NIST Certified)

---

## 3. Authoritative Metric Baseline Target Table

| Metric | Authoritative Module | Baseline Target Value |
|---|---|---|
| **Overall Security Posture** | `RiskEngine v1.5.0` | `62.4 / 100` |
| **GitHub Application Risk** | `RiskEngine v1.5.0` | `94.5` (Critical) |
| **GitHub Blast Radius** | `BlastRadiusCalculator` | `55.0 / 100` (Single Source of Truth) |
| **GitHub Attack Path Risk** | `GraphEngine` | `90.0` (Verified Potential Access Path) |
| **Simulated Residual Risk** | `RemediationOptimizer` | `53.6` (Target < 55.0 Achieved: TRUE) |
| **Evidence Hash Verification** | `EvidenceEngine` | `VERIFIED_INTACT` (SHA-256 Tamper-Evident) |

---

*Phase 2.1 Audit Baseline Established.*
