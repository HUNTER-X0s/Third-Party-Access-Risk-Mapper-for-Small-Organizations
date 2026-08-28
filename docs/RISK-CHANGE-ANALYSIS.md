# RISK CHANGE ANALYSIS SPECIFICATION
# AccessGuard: Deterministic "Why Did Risk Change?" Engine

**Document Type:** Technical Specification  
**Version:** 1.0  
**Status:** Approved & Implemented  

---

## 1. Overview

Given two security snapshots ($S_A$ and $S_B$), the **SnapshotEngine** performs deterministic risk-difference analysis to answer the fundamental operational question: **"Why did risk change?"**

---

## 2. Delta Computation

$$\Delta \text{Risk} = \text{Score}(S_B) - \text{Score}(S_A)$$

- `ESCALATED`: $\Delta \text{Risk} > 0$
- `IMPROVED`: $\Delta \text{Risk} < 0$
- `UNCHANGED`: $\Delta \text{Risk} = 0$

---

## 3. Primary Cause Classification

1. **Permission Expansion**: Detects added excess scopes ($S_B - S_A$).
2. **Critical Security Findings**: Detects new Critical severity findings.
3. **Remediation Revocation**: Detects removed excess scopes ($S_A - S_B$).
4. **Baseline Audit**: Records baseline configuration updates.
