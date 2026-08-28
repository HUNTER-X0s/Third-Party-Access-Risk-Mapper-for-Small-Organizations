# Phase 8 Security Review & Threat Model

**Phase:** Phase 8 — C-SCRM Supplier Risk & Due Diligence Governance  
**Date:** 2026-08-14  
**Status:** APPROVED & VERIFIED

---

## 1. Threat Model & Security Posture

| Threat Vector | Mitigation Strategy | Verification |
|---|---|---|
| **Cross-Tenant Supplier Profile Exposure** | Strict `organization_id` filtering in every DB query via `SupplierRiskEngine(db, org_id)` and tenant isolation tests. | Verified in `test_supplier_risk_isolation.py` |
| **Unauthorized Due Diligence Modification** | Server-side role enforcement requiring `SUPER_ADMIN`, `SECURITY_ADMIN`, or `IT_ADMIN`. `VIEWER` and `APP_OWNER` denied with 403. | Verified in `test_phase8_security_rbac.py` |
| **Supplier Assurance Suppressing Access Risk** | Access risk and supplier posture risk computed by isolated engines. High permission risk is NEVER reduced by good supplier assurance. | Verified in `SupplierRiskEngine` and UI components |
| **Unverified External Data Ingestion** | All imported subprocessor and supplier claims labeled `CLAIM` or `DECLARED` rather than `VERIFIED`. `is_synthetic_demo` flag explicitly attached. | Verified in `seed.py` and model defaults |
| **Due Diligence Assessment Tampering** | Immutable `SupplierAssessmentHistory` records appended upon every modification with user attribution and `AuditEvent` logging. | Verified in `test_vendor_model.py` |

---

## 2. NIST SP 1326 Compliance Governance

- Terminology: "aligned with NIST SP 1326", "mapped to NIST SP 800-161 Rev. 1", "synthetic demo".
- Absolute prohibition on claiming official government or third-party certification.
