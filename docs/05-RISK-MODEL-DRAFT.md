# 05 — Risk Model Specification (Hardened)
# AccessGuard: Dimensional Risk Engine, Mathematical Calibration & Versioning

**Document Type:** Risk Model Specification  
**Version:** 1.5  
**Date:** 2026-08-13  
**Status:** Hardened Specification  

---

## 1. Core Principles

1. **Determinism** — Identical inputs yield identical scores. Zero AI influence.
2. **Dimensional Separation** — Risk is calculated across 5 independent dimensions (Technical, Data Exposure, Business Impact, Vendor, Attack Path) before weighted aggregation.
3. **Audit Reproducibility** — Every finding is stamped with `risk_engine_version` (e.g. `v1.5.0`).
4. **Mathematical Calibration** — Formulas obey Monotonicity, Hierarchy Ordering, and Boundary Clamping.
5. **Data Quality Awareness** — Missing data defaults to conservative medium risk (50/100); stale data (>180d) incurs decay penalties.

---

## 2. Risk Score Range & Severity Levels

| Range | Severity | UI Badge Styling (AG-DS) | Required Action Window |
|---|---|---|---|
| 85 – 100 | **Critical** | Red (`bg-red-950/40 text-red-400 border-red-800`) | Immediate (24 Hours) |
| 65 – 84 | **High** | Orange (`bg-orange-950/40 text-orange-400 border-orange-800`) | 7 Days |
| 40 – 64 | **Medium** | Yellow (`bg-yellow-950/40 text-yellow-400 border-yellow-800`) | 30 Days |
| 15 – 39 | **Low** | Emerald (`bg-emerald-950/40 text-emerald-400 border-emerald-800`) | 90 Days |
| 0 – 14 | **Info** | Slate (`bg-slate-900 text-slate-400 border-slate-800`) | Monitor |

---

## 3. Dimensional Risk Structure & Formula

```
OverallRiskScore = clamp(0, 100, (
    TR * 0.30 + 
    DER * 0.25 + 
    BIR * 0.15 + 
    VSR * 0.15 + 
    APR * 0.15
) * ContextMultiplier)
```

### Dimensions:
- **Technical Risk (TR)**: Scope severity & excess privilege ratio.
- **Data Exposure Risk (DER)**: Maximum sensitivity of reachable data assets (1–5 scale).
- **Business Impact Risk (BIR)**: System of record criticality & regulated data multipliers.
- **Vendor & Supply Chain Risk (VSR)**: Vendor trust score (inverse), SOC 2 status & fourth-party depth.
- **Attack Path Risk (APR)**: Graph path exploitability, blast-radius asset count & path shortness.

---

## 4. Calibration Verification Vectors

The automated test suite runs against 4 canonical calibration vectors:

- `VEC-LOW` (Calendar App, matched purpose) → **Score 15 (Low)**
- `VEC-MED` (CRM sync app, 1 excess scope) → **Score 51 (Medium)**
- `VEC-HIGH` (Marketing app, undeclared Drive access) → **Score 76 (High)**
- `VEC-CRIT` (Shadow Zapier, admin scope, breach vendor, PII asset) → **Score 94 (Critical)**

---

*Risk Model Specification v1.5 — Hardened Specification.*
