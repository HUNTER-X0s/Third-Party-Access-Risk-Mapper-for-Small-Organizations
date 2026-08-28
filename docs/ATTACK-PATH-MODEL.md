# ATTACK PATH MODEL SPECIFICATION
# AccessGuard: Potential Access-Path Analysis & Graph Traversal

**Document Type:** Technical Specification  
**Version:** 1.0  
**Status:** Approved & Implemented  

---

## 1. Overview

AccessGuard models third-party access risks using **Potential Access Paths**. The system identifies valid traversal chains from external SaaS integrations to sensitive organizational data assets and business processes.

> **Terminology Rule:** The system identifies **POTENTIAL ACCESS PATHS**, not confirmed exploit chains, unless specific exploit evidence exists.

---

## 2. Path Schema & Node Structure

$$\text{EXTERNAL APPLICATION} \to \text{PERMISSION GRANT} \to \text{DATA ASSET} \to \text{BUSINESS PROCESS}$$

Each discovered path contains:
- `path_id`: Unique deterministic hash string.
- `entry_application`: Display name and ID of entry SaaS app.
- `target_data_asset`: Target data asset name and crown jewel flag.
- `business_process_impacted`: Impacted business process.
- `path_nodes`: Ordered array of graph nodes.
- `path_risk_score`: Deterministic path score (0–100).
- `contributors`: Factor breakdown.
- `confidence_percentage`: Evidence coverage percentage.
- `verification_state`: `VERIFIED` | `PARTIALLY VERIFIED` | `INFERRED`.

---

## 3. Path Scoring Formula

$$\text{Path Risk} = \min\left(100, S_{\text{entry}} + S_{\text{scope}} + S_{\text{excess}} + S_{\text{data}} + S_{\text{boundary}}\right)$$

- $S_{\text{entry}}$: +20 for Shadow App, +10 for External SaaS App.
- $S_{\text{scope}}$: +35 for Critical Scope (`organization_admin`), +25 for High Scope.
- $S_{\text{excess}}$: +15 for Excess Unjustified Scope.
- $S_{\text{data}}$: +25 for Crown Jewel Asset, $+3 \times \text{Sensitivity Level}$ for standard assets.
- $S_{\text{boundary}}$: +5 for crossing external trust boundary.

---

## 4. Cycle Prevention & Traversal Safety

- Maximum path depth is strictly limited to **6 hops**.
- Visited node tracking prevents infinite loops and graph cycles.
- Traversal runs in $O(V + E)$ bounded time using BFS/DFS.
