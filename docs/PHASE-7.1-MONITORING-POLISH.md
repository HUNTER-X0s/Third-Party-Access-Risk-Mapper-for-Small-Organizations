# Phase 7.1 — Continuous Monitoring Polish, Graph Delta & Notification Center

## Executive Summary

Phase 7.1 completes the operational monitoring loop of AccessGuard by delivering:
1. **Graph Change Visualization**: Direct visual inspection of NEW, CHANGED, REMOVED, and UNCHANGED access topology edges.
2. **In-Process Periodic Scheduler**: Thread-safe continuous evaluation engine with concurrency overlap protection and full audit trails.
3. **In-App Notification Center**: High-density alerts console with deterministic SHA-256 fingerprint deduplication, unread badges, and deep-link investigation workflows.
4. **End-to-End Consistency**: Unified referencing of entity IDs across Monitoring, Graph, Notifications, Risk, and AI Advisory subsystems.

---

## Deliverables Summary

| Area | Component | Description |
|---|---|---|
| **Graph Delta** | `GET /api/v1/graph/delta` | Annotated topology with `change_status` (NEW, REMOVED, CHANGED, UNCHANGED) |
| **Graph UI** | `AccessGraphView.tsx` | Mode toggle (`DELTA`, `CURRENT`, `BASELINE`), edge highlighting, legend, and inspection drawer |
| **Scheduler** | `MonitoringScheduler` | In-process worker thread, overlap locking, config-driven (`MONITORING_INTERVAL_SECONDS=900`) |
| **Manual Trigger** | `POST /api/v1/monitoring/run` | Server-authorized evaluation trigger (SECURITY_ADMIN / IT_ADMIN) |
| **Notifications** | `SecurityNotification` | Deduplicated alert records with SHA-256 fingerprint |
| **Notification Center** | `NotificationCenter.tsx` | Navbar badge, filterable alerts dropdown, mark-read actions |
| **Monitoring Hub** | `MonitoringPage.tsx` | Real-time scheduler status banner, KPI strip, Changes/Incidents/Alerts tabs |

---

## Architectural Boundaries

- **Deterministic Core**: GraphEngine, RiskEngine v1.5.0, and SecurityDiffEngine remain strictly deterministic.
- **AI Layer**: Remains read-only and advisory; AI does not calculate deltas, mutate notifications, or set severity.
- **Tenant Isolation**: Row-level tenant isolation enforced on every notification, change, incident, and graph query.
