# PHASE 2 SECURITY GRAPH INTELLIGENCE REPORT
# AccessGuard: Attack Path Analysis, Blast Radius & Snapshot Intelligence

**Document Type:** Phase 2 Technical Architecture & Intelligence Report  
**Version:** 2.0  
**Date:** 2026-08-13  
**Status:** Implemented & 100% Verified  

---

## 1. Executive Summary

Phase 2 transforms **AccessGuard** from a static application and permission inventory into an authoritative **Security Graph Intelligence & Attack Path Analysis Platform**.

By leveraging pure Python graph traversal (`GraphEngine`), deterministic blast-radius calculations (`BlastRadiusCalculator`), lightweight security state snapshots (`SnapshotEngine`), and bounded remediation optimization (`RemediationOptimizer`), AccessGuard extracts deep security intelligence from authorized third-party SaaS integration data—without using unexplainable AI models or external network dependencies.

---

## 2. Implemented Capabilities

### 2.1 Backend Graph Reasoning & Taxonomy (`app/services/graph_engine.py`)
- **Node Taxonomy**: `ORG`, `APP`, `VENDOR`, `PERMISSION`, `DATA_ASSET`, `BUSINESS_PROCESS`, `DEPARTMENT`, `TRUST_BOUNDARY`.
- **Edge Taxonomy**: `OWNS`, `USES`, `GRANTS`, `HAS_PERMISSION`, `ACCESSES`, `FLOWS_TO`, `BELONGS_TO`, `PROCESSES`, `CROSSES_BOUNDARY`, `DEPENDS_ON`.
- **Traversal Algorithm**: BFS/DFS algorithm with visited set tracking and a maximum depth limit of 6 to prevent infinite loop cycles.
- **Tenant Isolation**: Every graph query enforces strict `organization_id` filters. Cross-tenant traversal is mathematically impossible.

### 2.2 Potential Attack-Path Analysis (`GET /api/v1/graph/paths`)
- Discovers deterministic access paths mapping `Entry Application → Scope → Sensitive Data Asset → Crown Jewel → Business Process`.
- Calculates explainable Path Risk Scores (0–100) with factor contributors.
- Evaluates **Path Confidence** (0–100%) and **Evidence Coverage Ratio** (e.g., 3/3 links verified → `VERIFIED` state).

### 2.3 Blast-Radius Calculator (`GET /api/v1/graph/blast-radius/{app_id}`)
- Calculates reachable data assets, crown jewels, impacted business processes, exposed user accounts, and departments.
- Produces normalized Blast Radius Score (0–100) with factor decomposition (+30 Crown Jewel, +20 multiple assets, +20 critical processes, +15 shadow app).

### 2.4 Security Snapshots & Risk-Change Analysis (`GET /api/v1/snapshots/{id}/compare/{other_id}`)
- Captures lightweight state manifests (`SecuritySnapshot`).
- Performs deterministic risk-difference analysis (`42.0 → 62.4 (+20.4)`), classifying primary causes (`Permission Expansion`, `Critical Security Finding`, `Remediation Revocation`) without AI.

### 2.5 Minimum Effective Remediation (`GET /api/v1/findings/{id}/remediation-analysis`)
- Bounded combinatorial optimization finding candidate scope revocations that lower overall risk score below target threshold (e.g. Risk < 50.0).
- Reports predicted residual risk, attack path reduction, and blast radius reduction with explicit `SIMULATION ONLY` warning tags.

---

## 3. Verification & Test Summary

- **Backend Pytest Suite**: 36 passed out of 36 tests (**100% pass rate in 7.75s**).
- **Phase 1 Regression Scenario**: 20-step scenario passed 100%.
- **Phase 2 Central Demo Scenario**: *"What happens if GitHub is compromised?"* passed 100%.
- **Frontend Production Build**: `npm run build` completed with 0 errors.

---

*Phase 2 Security Graph Intelligence Report — Complete & Verified.*
