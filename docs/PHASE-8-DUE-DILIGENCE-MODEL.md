# Phase 8 Due Diligence Model Specification

**Status:** Authoritative  
**Alignment:** NIST SP 1326 (Supply Chain Due Diligence Guide)  
**Standard Elements:** FOCI, Provenance, Resilience, Foundational Cyber Practices, Supply Chain Tiers

---

## 1. Due Diligence Dimensions & Penalties

| Dimension | States & Weights | Scoring Notes |
|---|---|---|
| **FOCI** | `ASSESSED_NO_CONCERN` (0 pts)<br>`POTENTIAL_CONCERN` (25 pts)<br>`UNKNOWN` (15 pts)<br>`NOT_ASSESSED` (20 pts) | Evaluates foreign corporate control or governance influence. |
| **Provenance** | `ASSESSED` (0 pts)<br>`CLAIM` (10 pts)<br>`UNKNOWN` (15 pts)<br>`DISPUTED` (25 pts) | Tracks verified origin country, ownership, and hosting infrastructure. |
| **Resilience** | `CURRENT` (0 pts)<br>`ASSESSED` (5 pts)<br>`GAP` (20 pts)<br>`UNKNOWN` (15 pts) | Assesses SLA availability, BCP/DR documentation, and backup testing (+5 penalty if not tested). |
| **Cyber Practices** | `STRONG` (0 pts)<br>`PARTIAL` (10 pts)<br>`MINIMAL` (20 pts)<br>`UNKNOWN` (15 pts) | Evaluates verifiable controls: MFA enforcement (+5 penalty if missing), vulnerability management, encryption, and tested incident response. |

---

## 2. Calculation Formula

$$\text{RawScore} = \text{Score}_{\text{FOCI}} + \text{Score}_{\text{Prov}} + \text{Score}_{\text{Res}} + \text{Score}_{\text{Cyber}}$$
$$\text{SupplierRiskScore} = \text{round}(\text{clamp}(\text{RawScore}, 5.0, 95.0), 1)$$

### Severity Mapping:
- **Critical**: $\text{Score} \ge 80.0$
- **High**: $60.0 \le \text{Score} < 80.0$
- **Medium**: $30.0 \le \text{Score} < 60.0$
- **Low**: $\text{Score} < 30.0$

---

## 3. Immutability and Audit Logging

Every update to due diligence records:
1. Captures a full snapshot of the previous state in `SupplierAssessmentHistory`.
2. Increments `version`.
3. Sets `reviewed_by` to the authenticated user's email.
4. Generates an `AuditEvent` with action `SUPPLIER_ASSESSMENT_UPDATED`.
