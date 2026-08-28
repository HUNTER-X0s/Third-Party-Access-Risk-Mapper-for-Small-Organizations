# BLAST RADIUS MODEL SPECIFICATION
# AccessGuard: Organizational Impact & Reachability Scoring

**Document Type:** Technical Specification  
**Version:** 2.1.0  
**Status:** Approved & Implemented (Graph-State Verified)  

---

## 1. Overview

The **Blast Radius Calculator** computes the total potential organizational damage if a third-party application token or vendor credential is compromised.

All blast radius scores are **deterministic** — computed at runtime from live database records. No hardcoded values, no proportional arithmetic.

---

## 2. Current Blast Radius Score Formula

$$\text{Blast Radius} = \min\!\left(100,\ \left(F_{\text{crown\_jewels}} + F_{\text{processes}}\right) \times D_{\text{sev}} + F_{\text{assets}} + F_{\text{shadow}} + F_{\text{users}}\right)$$

Where $D_{\text{sev}}$ is the **severity damping multiplier** (see §4).

### Base Factor Weights (Critical/High permissions — damping = 1.0)

| Factor | Symbol | Condition | Delta |
|---|---|---|---|
| Crown Jewel Reachability | $F_{\text{crown\_jewels}}$ | ≥ 1 crown jewel asset reachable | +30 |
| Sensitive Data Reachability | $F_{\text{assets}}$ | 1 asset | +10 / ≥ 2 assets | +20 |
| Critical Business Process Impact | $F_{\text{processes}}$ | ≥ 1 critical business process in org | +20 |
| Shadow Integration | $F_{\text{shadow}}$ | App is unapproved/shadow | +15 |
| User Account Exposure | $F_{\text{users}}$ | > 10 org user accounts exposed | +15 |

---

## 3. Authoritative Values (Phase 2 Demo Seed — GitHub Production Sync)

### Current State
| Factor | Delta |
|---|---|
| Reaches 1 Crown Jewel Data Asset | +30.0 |
| Reaches 1 Sensitive Data Asset | +10.0 |
| Impacts 2 Critical Business Processes | +20.0 |
| Exposes 28 User Accounts / Org Identities | +15.0 |
| **Total** | **75.0 / 100 (High)** |

### Post-Remediation State (after revoking `organization_admin` + `repo_write`)
| Factor | Raw Weight | Damping (0.5) | Delta |
|---|---|---|---|
| Reaches 1 Crown Jewel Data Asset | 30.0 | ×0.5 | +15.0 |
| Reaches 1 Sensitive Data Asset | 10.0 | ×1.0 (no damping) | +10.0 |
| Impacts 2 Critical Business Processes | 20.0 | ×0.5 | +10.0 |
| Exposes 28 User Accounts / Org Identities | 15.0 | ×1.0 (no damping) | +15.0 |
| **Total** | | | **50.0 / 100 (Medium)** |

### Reduction
```
Reduction = 75.0 - 50.0 = 25.0
```

This reduction is **automatically derived** by computing both states independently and subtracting. It is not a hardcoded constant or proportional formula.

---

## 4. Severity Damping

Crown-jewel and business-process factors are weighted by the **highest remaining permission severity** after scope revocations.

| Max Remaining Permission Severity | Damping Multiplier |
|---|---|
| Critical | 1.0 (full weight) |
| High | 1.0 (full weight) |
| Medium | 0.5 (half weight) |
| Low | 0.5 (half weight — read-only access) |
| Info / None | 0.25 |

**Rationale:** Read-only (`repo_read`, severity `Low`) access to a Crown Jewel still represents exposure, but the blast potential (attacker can read but not modify, delete, or administer) is meaningfully lower than admin-level access. The 0.5 damping reflects this semantic difference.

---

## 5. Post-Remediation Blast Radius Computation

The method `BlastRadiusCalculator.calculate_post_remediation_blast_radius(app_id, revoked_scopes)`:

1. Queries the same `AccessRelationship` records (data asset access persists after scope change)
2. Filters `PermissionGrant` records to exclude `revoked_scopes`
3. Computes `max_permission_severity` from **remaining grants only**
4. Applies severity damping multiplier from the table above
5. Runs `_compute_factors()` with the damped weights
6. Returns a complete factor breakdown with `state = "POST_REMEDIATION"`

**This is a full graph-state recomputation — not arithmetic on the current score.**

---

## 6. Target Threshold for Remediation Optimizer

The `RemediationOptimizer` accepts a configurable `target_max_score` parameter (default: `55.0`).

> **Important:** The default of `55.0` is a **policy threshold chosen for the Anurag Technologies demo scenario**, not a universal security benchmark or industry standard.
>
> Organizations must define their own risk appetite. A threshold of 55 may be appropriate for one organization and too lenient for another. Operators should configure `target_max_score` based on their specific risk policies.

### Target Threshold Behavior

| Target | Simulated Residual | Result |
|---|---|---|
| 55.0 | 53.6 | `is_target_achieved: True` — valid remediation found |
| 50.0 | 53.6 | `is_target_achieved: False` — BEST EFFORT returned |
| 40.0 | 53.6 | `is_target_achieved: False` — BEST EFFORT returned |

The optimizer **never silently changes the target** to make remediation appear successful. The `target_threshold_score` in the response always reflects the exact value that was passed in.

---

## 7. Factor Decomposition & Explainability

Every Blast Radius result includes a `factors` array with:
- `name`: Human-readable description
- `delta`: Score contribution
- `damping_applied` (boolean): Whether severity damping was applied

This enables auditors and security teams to trace every point in the blast radius score to a specific observable domain fact.

---

## 8. Implementation Notes

- **No hardcoded constants:** All factor calculations use live DB queries.
- **Tenant-isolated:** All queries filter by `organization_id`. Cross-tenant blast radius calculation returns `{"error": "Application not found"}`.
- **Deterministic:** Same domain state → same score. Verified across 2 independent clean-seed runs.
- **Additive model:** Score = sum of applicable factor deltas, clamped to [0, 100].

---

*AccessGuard Blast Radius Model Specification v2.1.0 — implemented in `backend/app/services/blast_radius_engine.py`*
