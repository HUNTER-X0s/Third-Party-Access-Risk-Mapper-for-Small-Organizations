# NIST Cyber Supply Chain Risk Management (C-SCRM) References & Alignment

**Document Type:** Standards Reference & Alignment Mapping  
**Framework Baseline:** NIST SP 1326 (Final, July 2026), NIST SP 800-161 Rev. 1, NIST SP 800-18 Rev. 2 (Final, June 2026), NIST CSF 2.0 (GV.SC)  
**Status:** REFERENCE ONLY — ALIGNED / MAPPED (NO COMPLIANCE OR CERTIFICATION CLAIMS)

---

## 1. Primary Standards Sources of Truth

### NIST SP 1326 (Final, July 2026): Supply Chain Due Diligence: A Guide for Federal and Critical Infrastructure Entities
- **Source:** National Institute of Standards and Technology (NIST)
- **Core Due Diligence Components:**
  1. **Foreign Ownership, Control, or Influence (FOCI)**: Evaluation of recorded foreign corporate ownership, governance influence, or jurisdictions of primary operational control based on verified filings.
  2. **Provenance**: Verification of product/service origins, hosting infrastructure locations, codebase ownership, and authentic build chains.
  3. **Resilience**: Service availability assurances, business continuity / disaster recovery (BCP/DR) plans, backup verifications, and operational concentration limits.
  4. **Foundational Cyber Practices**: Verifiable baseline controls (MFA enforcement, vulnerability management, security disclosures, encryption at rest/transit, incident response capabilities).
  5. **Supply Chain Tiers**: Visibility into Tier 1 (Direct Supplier), Tier 2 (Critical Subprocessors), and Tier 3+ (Downstream Hosting / Infrastructure).

### NIST SP 800-161 Rev. 1: Cybersecurity Supply Chain Risk Management Practices for Systems and Organizations
- Multi-tiered risk assessment, supplier criticality tiering, continuous monitoring, and evidence-grounded assessment freshness.

### NIST SP 800-18 Rev. 2 (Final, June 2026): Guide for Developing Security and Privacy Plans
- Documentation of external service provider boundaries, system interconnections, and responsible personnel.

---

## 2. Four-Domain Scored vs Five-Component Structural Model

> **Architectural Alignment Note:**  
> AccessGuard scores **selected due-diligence evidence domains** (FOCI, Provenance, Resilience, Foundational Cyber Practices) while modeling **Supply Chain Tiers** as a separate structural dimension across the graph and subprocessor hierarchy.

---

## 3. Scope of Implementation & Indicators

| NIST Component | AccessGuard Implementation | Scope & Indicator Status |
|---|---|---|
| **FOCI** | `SupplierDueDiligence.foci_status` (`ASSESSED_NO_CONCERN`, `POTENTIAL_CONCERN`, `UNKNOWN`, `NOT_ASSESSED`) | **PARTIAL**: Assesses documented corporate evidence; does NOT make unsupported legal, political, or jurisdictional conclusions. Incomplete data is labeled `UNKNOWN`, not assumed concern. |
| **Provenance** | `SupplierDueDiligence.provenance_status`, `service_origin_country`, `hosting_provider` | **PARTIAL**: Distinguishes `CLAIM` (supplier-provided declaration) from `ASSESSED` (observed evidence) and `UNKNOWN`. |
| **Resilience** | `SupplierDueDiligence.resilience_status`, `sla_availability_pct`, single-supplier failure impact simulator | **SELECTED RESILIENCE EVIDENCE**: Covers SLA %, documented BCP/DR, and tested backup recovery. Does NOT claim complete resilience assessment. |
| **Foundational Cyber Practices** | `SupplierDueDiligence.cyber_practices_status`, `mfa_enforced`, `vuln_mgmt_documented`, `incident_response_tested` | **SELECTED FOUNDATIONAL CYBER PRACTICE INDICATORS**: Focuses on MFA enforcement, vulnerability management, and tested incident response. Does NOT claim full NIST Foundational Cyber Practices coverage. |
| **Supply Chain Tiers** | `SupplierSubprocessor` (Tiers 1, 2, 3) with `verification_status` (`DECLARED`, `VERIFIED`, `INFERRED`) | **STRUCTURAL MODEL**: Models downstream subprocessor trees in the Access Graph with declared vs verified boundary tags. |

---

## 4. Governance Boundaries & Safe Terminology

- AccessGuard uses **"ALIGNED WITH NIST SP 1326 / NIST SP 800-161"** instead of claiming compliance or certification.
- Unverified supplier claims are stored as `CLAIM` rather than `VERIFIED`.
- Unknown due-diligence data is explicitly classified as `UNKNOWN` rather than default low risk.
- Demo data is explicitly tagged with `is_synthetic_demo = True` and labeled `SYNTHETIC DEMO DATA`.
