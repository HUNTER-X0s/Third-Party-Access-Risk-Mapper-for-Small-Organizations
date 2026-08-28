# REMEDIATION OPTIMIZATION SPECIFICATION
# AccessGuard: Minimum Effective Remediation & Bounded Optimization

**Document Type:** Technical Specification  
**Version:** 2.1.0  
**Status:** Approved & Implemented (Graph-State Verified)  

---

## 1. Overview

The **RemediationOptimizer** evaluates candidate scope revocation subsets for security findings to recommend the **Minimum Effective Remediation**—the smallest practical permission removal that lowers risk score below a configurable target threshold (e.g. Risk ≤ 55.0).

---

## 2. Configurable Target Threshold & Policy Clarification

The `RemediationOptimizer` accepts an explicit `target_max_score` parameter (default `55.0`).

> **Important Policy Clarification:**
> The default target threshold of `55.0` is a **configurable policy threshold chosen for the Anurag Technologies demo scenario**, NOT a universal security standard or industry benchmark.
> 
> Security policies vary by organization and risk appetite. The optimizer supports arbitrary configurable thresholds (e.g., 50.0, 55.0, 40.0).

### Target Evaluation Behavior
- **If Achievable:** Returns `is_target_achieved: True` with the minimal revocation scope candidate that satisfies $\text{Simulated Score} \le \text{Target Threshold}$.
- **If Not Achievable:** Returns `is_target_achieved: False` with the lowest-scoring candidate labeled `(BEST EFFORT - TARGET UNMET)`.
- **Target Integrity:** The optimizer **never** silently alters the target threshold to force a successful status.

---

## 3. Post-Remediation Blast Radius (Graph-State Derived)

Post-remediation blast radius before and after values are calculated directly via `BlastRadiusCalculator.calculate_post_remediation_blast_radius()`.

- **Current Blast Radius:** $75.0 / 100$ (High)
- **Post-Remediation Blast Radius:** $50.0 / 100$ (Medium)
- **Reduction:** $25.0$ (automatically derived: $75.0 - 50.0$)

No proportional arithmetic or static hardcoded values are used.

---

## 4. Candidate Evaluation Algorithm

For a finding with excess scopes:
1. **Candidate 1:** Revoke primary excess scope ($S_1$).
2. **Candidate 2:** Revoke all excess scopes ($S_{\text{all}}$).
3. Recalculate simulated risk score and graph-state post-remediation blast radius for each candidate.
4. Select the candidate with the smallest scope set that satisfies $\text{Simulated Score} \le \text{Target Threshold}$. If none satisfy the target, select the best-effort candidate with `is_target_achieved: False`.

---

## 5. Mandatory Safety & Simulation Labeling

All recommendations and simulation outputs carry mandatory warning tags:
`⚡ SIMULATION ONLY — NO PROVIDER CHANGES EXECUTED`

---

*AccessGuard Remediation Optimization Specification v2.1.0 — implemented in `backend/app/services/remediation_optimizer.py`*
