# RISK CALIBRATION & HARDENING FRAMEWORK
# AccessGuard: Mathematical Properties, Calibration Vectors & Dimensional Separation

**Document Type:** Technical Specification  
**Version:** 1.0  
**Date:** 2026-08-13  
**Status:** Approved Risk Specification  

---

## 1. Dimensional Separation of Risk

To avoid obscuring critical security nuances, AccessGuard calculates **5 distinct Risk Dimensions** before aggregating them into the overall Application Risk Score.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ACCESSGUARD RISK ENGINE                         │
├──────────────┬──────────────────┬─────────────────┬───────────────────┤
│ TECHNICAL    │ DATA EXPOSURE    │ BUSINESS IMPACT │ VENDOR & SUPPLY   │
│ RISK (TR)    │ RISK (DER)       │ RISK (BIR)      │ CHAIN RISK (VSR)  │
│ [Max Scope & │ [Reachable PII/  │ [Criticality of │ [Breach History,  │
│ Admin Priv]  │ Financial Assets]│ Process & Org]  │ SOC2 & Country]   │
├──────────────┴──────────────────┴─────────────────┴───────────────────┤
│                        ATTACK PATH RISK (APR)                          │
│        [Graph Reachability, Chained Scopes & Exploitability]          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
                 OVERALL APPLICATION RISK SCORE (0–100)
```

---

## 2. Dimensional Formulas

### 2.1 Technical Risk (TR) — Weight: 0.30
Evaluates raw permission privilege severity and excess permissions.
$$\text{TR} = \max(\text{Severity}_{\text{granted}}) \times 0.60 + (\text{ExcessRatio} \times 100) \times 0.40$$

### 2.2 Data Exposure Risk (DER) — Weight: 0.25
Evaluates the maximum sensitivity of data assets reachable via current permissions.
$$\text{DER} = \max(\text{SensitivityScore}(\text{asset}_k) \text{ for asset}_k \in \text{ReachableAssets})$$

### 2.3 Business Impact Risk (BIR) — Weight: 0.15
Evaluates the operational criticality of the connected data asset and system of record.
$$\text{BIR} = \text{CriticalityScore}(\text{SystemOfRecord}) \times \text{RegulatedDataMultiplier}$$

### 2.4 Vendor & Supply Chain Risk (VSR) — Weight: 0.15
Evaluates vendor trust, SOC 2 posture, breach history, and fourth-party dependencies.
$$\text{VSR} = (100 - \text{VendorTrustScore}) \times 0.70 + (\text{FourthPartyDepth} \times 10) \times 0.30$$

### 2.5 Attack Path Risk (APR) — Weight: 0.15
Evaluates graph reachability from entry point to crown jewel assets.
$$\text{APR} = \text{PathExploitability} \times \text{BlastRadiusAssetCount} \times \text{PathShortnessFactor}$$

---

## 3. Overall Score Aggregation & Formula Versioning

The Overall Application Risk Score is computed deterministically:
$$\text{OverallRiskScore} = \text{clamp}_{0}^{100} \left( \sum_{d \in \text{Dimensions}} (\text{Score}_d \times \text{Weight}_d) \times \text{ContextMultiplier} \right)$$

### Engine Versioning:
Every calculation output stamps `risk_engine_version: "v1.5.0"`. If formula weights or factors change via a DECISION-LOG entry, the version increments (`v1.6.0`), preserving audit reproducibility.

---

## 4. Mathematical Calibration Properties

The risk engine MUST pass automated unit tests verifying the following 5 mathematical properties:

### Property 1: Strict Monotonicity
- **Rule**: Adding an excessive permission or increasing data sensitivity MUST NEVER decrease the risk score.
- **Assertion**: $\text{Risk}(P \cup \{p_{\text{excess}}\}) \ge \text{Risk}(P)$

### Property 2: Scope Hierarchy Ordering
- **Rule**: Permissions MUST obey action severity hierarchy: $\text{READ} < \text{WRITE} < \text{EXPORT} < \text{ADMIN}$.
- **Assertion**: $\text{TR}(\text{Mail.Read}) < \text{TR}(\text{Mail.ReadWrite}) < \text{TR}(\text{Mail.Send}) < \text{TR}(\text{Directory.AccessAsApp.All})$

### Property 3: Boundary Clamping
- **Rule**: Scores MUST stay strictly within $[0, 100]$.
- **Assertion**: $0 \le \text{RiskScore} \le 100$ for all valid and extreme inputs.

### Property 4: Graceful Missing Data Handling
- **Rule**: If vendor SOC 2 status is `UNKNOWN`, the engine MUST default to a conservative medium risk modifier (50/100), rather than 0 (optimistic) or failing.

### Property 5: Stale Data Penalty
- **Rule**: Unreviewed access older than 180 days incurs a linear decay penalty (+0.1 risk score per day past 180 days, capped at +20).

---

## 5. Deterministic Reference Test Vectors

The risk engine test suite executes against these 4 canonical calibration vectors:

| Vector ID | Scenario | Expected Severity | Expected Score Range | Key Factor Driver |
|---|---|---|---|---|
| `VEC-LOW` | Read-only Calendar app, declared purpose matched, SOC 2 vendor | **Low** | 10 – 25 | Low scope severity, zero excess |
| `VEC-MED` | CRM contact sync app, 1 excess scope (`read_user_directory`), clean vendor | **Medium** | 42 – 58 | Moderate excess privilege |
| `VEC-HIGH` | Marketing email sender with undeclared `read_files` access to Google Drive | **High** | 68 – 82 | High data exposure + excess |
| `VEC-CRIT` | Shadow Zapier integration with `admin:org` + breach history vendor + PII asset | **Critical** | 88 – 98 | Shadow status + Admin scope + Breach history |

---

*Risk Calibration Framework v1.0 — Approved Specification.*
