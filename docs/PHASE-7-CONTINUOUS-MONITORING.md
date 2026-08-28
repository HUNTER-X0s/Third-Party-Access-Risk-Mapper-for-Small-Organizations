# Phase 7 — Continuous Third-Party Access Monitoring

## Overview

AccessGuard Phase 7 transforms the platform from a point-in-time assessment tool into a **continuous, deterministic third-party access intelligence system**. The system can now detect permission changes, identify Shadow SaaS applications, correlate security incidents, and calculate risk delta across time — all using deterministic engines with no AI involvement in security-critical computations.

---

## Central Pipeline

```
PREVIOUS TRUSTED SNAPSHOT
          ↓
CURRENT CONNECTOR SNAPSHOT
          ↓
SecurityDiffEngine.compare_snapshots()
          ↓
SecurityChangeSet (ADDED / REMOVED / CHANGED)
          ↓
Impact Analysis: Crown Jewels · Attack Paths · Blast Radius
          ↓
Risk Delta (RiskEngine — deterministic)
          ↓
New / Resolved Findings
          ↓
SecurityIncident (Correlated)
          ↓
In-App Alerts
          ↓
Remediation linkage
          ↓
AI Analyst explanation (advisory only)
```

---

## Architecture Components

### SecurityDiffEngine
`backend/app/services/diff_engine.py`

- Compares Snapshot A vs Snapshot B using stable application IDs, canonical permission identifiers, and relationship identifiers.
- Produces granular `SecurityChange` records per event.
- Correlates child changes into a `SecurityIncident`.
- **Fully deterministic**: identical inputs produce identical outputs.

### SecurityChange Model
`backend/app/models/monitoring.py`

| Field | Description |
|---|---|
| `id` | UUID |
| `organization_id` | Tenant isolation key |
| `snapshot_before_id` | Reference to trusted Snapshot A |
| `snapshot_after_id` | Reference to trusted Snapshot B |
| `change_type` | Taxonomy (see SECURITY-DIFF-MODEL.md) |
| `object_type` | APPLICATION / PERMISSION / DATA_ASSET / FINDING / ORGANIZATION |
| `object_id` | Stable identifier of the changed entity |
| `severity` | Critical / High / Medium / Low / Info |
| `confidence` | VERIFIED / HIGH / MEDIUM / LOW |
| `evidence_refs` | Before/after evidence IDs |
| `impact_summary` | Deterministic human-readable description |
| `status` | NEW / REVIEWED / ACKNOWLEDGED / RESOLVED |

### SecurityIncident Model
Correlated event grouping multiple related changes from one synchronization run.

### ApplicationBaseline Model
Lightweight approved access record for each application enabling Authorized vs Observed comparisons.

---

## Connector Integration

When a connector sync runs:
1. Previous trusted snapshot is retrieved.
2. New snapshot is created after normalization.
3. `SecurityDiffEngine.compare_snapshots()` runs automatically.
4. Detected changes are persisted as `SecurityChange` records.
5. A `SecurityIncident` is created grouping all correlated changes.

If a sync fails, the previous trusted snapshot is preserved; no false changes are created.

---

## REST API Endpoints

| Endpoint | Auth | Description |
|---|---|---|
| `GET /api/v1/monitoring/changes` | All roles | Filterable security change timeline |
| `GET /api/v1/monitoring/incidents` | All roles | Correlated security incidents |
| `POST /api/v1/monitoring/incidents/{id}/status` | SECURITY_ADMIN+ | Update incident lifecycle status |
| `GET /api/v1/monitoring/shadow-saas` | All roles | Approved vs Observed application inventory |
| `POST /api/v1/monitoring/applications/{id}/approve` | SECURITY_ADMIN+ | Approve or restrict application baseline |
| `GET /api/v1/monitoring/timeline` | All roles | Unified access security timeline |

---

## Demo Scenario: Phase 7 Canonical

1. **Snapshot A**: GitHub has `repo_read` only. Risk = 42.0.
2. **Provider state change**: GitHub gains `repo_write` + `organization_admin`.
3. **Snapshot B**: Created after sync. Risk = 94.5.
4. **Diff Engine** detects:
   - `PERMISSION_ESCALATED` (Critical) — `organization_admin`
   - `PERMISSION_ESCALATED` (High) — `repo_write`
   - `CROWN_JEWEL_REACHABILITY_CREATED` (Critical)
   - `RISK_INCREASED` (Critical, +52.5)
5. **SecurityIncident** created. Status = OPEN.
6. **Dashboard alert**: "Critical permission escalation — GitHub 3h ago"
7. **AI Analyst** (advisory): Explains permission expansion and risk delta when queried.

---

## Limitations

- Manual sync required (periodic sync is configurable but no external scheduler).
- AI explanation is advisory only and requires a live `GEMINI_API_KEY`.
- Email/SMS alerting not yet implemented (in-app only).
