# SECURITY SNAPSHOT MODEL SPECIFICATION
# AccessGuard: Security State Manifests & Timeline Snapshots

**Document Type:** Technical Specification  
**Version:** 1.0  
**Status:** Approved & Implemented  

---

## 1. Overview

A **SecuritySnapshot** represents an organization's third-party risk posture state at a specific point in time.

---

## 2. Snapshot Manifest & Versioning

Each snapshot captures:
- `id`, `organization_id`, `created_at`, `snapshot_label`, `trigger_reason`.
- Aggregate metrics: `security_posture_score`, `total_applications`, `critical_findings_count`, `high_findings_count`, `excess_permissions_count`, `crown_jewels_exposed_count`.
- `risk_engine_version`: Version stamp (e.g. `v1.5.0`).
- `state_manifest_json`: Lightweight reference dictionary containing app IDs, granted scopes, and active finding titles.
