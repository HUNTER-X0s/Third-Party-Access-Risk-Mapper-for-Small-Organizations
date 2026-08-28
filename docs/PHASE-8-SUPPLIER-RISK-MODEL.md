# Phase 8 Supplier Risk Model Specification

**Status:** Authoritative  
**Alignment:** NIST SP 1326, NIST SP 800-161 Rev. 1  
**Constraint:** Deterministic scoring only. AI model outputs are strictly advisory and never compute risk scores (AGENTS.md Rule 4 & 5).

---

## 1. Separation of Concerns: Access Risk vs Supplier Risk

AccessGuard maintains two independent risk dimensions for every third-party relationship:

```
┌─────────────────────────────────────────────────────────────┐
│                    THIRD-PARTY RISK POSTURE                 │
├──────────────────────────────┬──────────────────────────────┤
│       ACCESS RISK            │       SUPPLIER RISK          │
│  (RiskEngine v1.5.0)         │   (SupplierRiskEngine)       │
├──────────────────────────────┼──────────────────────────────┤
│ • OAuth scope elevation      │ • FOCI concerns (foreign     │
│ • Crown jewel reachability   │   control/influence)         │
│ • Attack path depth          │ • Provenance (origin/hosting)│
│ • Remediation actions        │ • Resilience & SLA posture   │
│ • Data exposure levels       │ • Foundational cyber controls│
│ • Permission excess          │ • Subprocessor dependencies  │
└──────────────────────────────┴──────────────────────────────┘
```

> **Non-Suppression Invariant:** High access risk (e.g., administrative access to customer PII) cannot be lowered or suppressed because a vendor possesses a strong security certification or low supplier risk score.

---

## 2. Supplier Criticality Evaluation

Criticality is evaluated deterministically from business process reliance and crown jewel reachability:

| Criticality Tier | Criteria |
|---|---|
| **CRITICAL** | Direct access to any Crown Jewel data asset, OR dependency for business processes with `criticality == CRITICAL`. |
| **HIGH** | 2+ connected applications OR any application with `risk_severity` in ("Critical", "High"). |
| **MEDIUM** | Single active application with Medium or Low risk severity. |
| **LOW** | Dormant integration or no active reachability. |

---

## 3. Dependency Concentration Scoring

Concentration measures the systemic risk of over-reliance on a single vendor across the organization:

$$\text{Score} = \min\left(100.0, (\text{Apps} \times 20.0) + (\text{CrownJewels} \times 30.0) + (\text{AssetConcentrationPct} \times 0.4)\right)$$

| Concentration Level | Score Range | Operational Meaning |
|---|---|---|
| **CRITICAL** | $\ge 75.0$ | Excessive systemic dependency. Single vendor failure impacts multiple critical processes. |
| **HIGH** | $50.0 - 74.9$ | Significant concentration. Failover procedures strongly recommended. |
| **MEDIUM** | $25.0 - 49.9$ | Moderate concentration across several assets. |
| **LOW** | $< 25.0$ | Distributed risk across vendors. |

---

## 4. Priority Queue Ranking (P0 / P1 / P2)

- **P0 (Immediate Action)**: Critical supplier with Crown Jewel access AND elevated access risk ($\ge 80.0$), OR high-criticality supplier with overdue/stale assessment.
- **P1 (Scheduled Review)**: Supplier with access risk $\ge 60.0$ OR supplier risk score $\ge 60.0$, OR upcoming review due soon.
- **P2 (Routine Monitoring)**: Low exposure supplier with current due diligence.
