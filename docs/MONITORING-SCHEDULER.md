# Monitoring Scheduler Architecture & Specification

## Overview

The `MonitoringScheduler` (`backend/app/services/monitoring_scheduler.py`) provides in-process, thread-safe periodic evaluation of continuous access security intelligence.

---

## Configuration Settings

| Variable | Type | Default | Description |
|---|---|---|---|
| `MONITORING_ENABLED` | bool | `False` | Enables/disables the background worker thread |
| `MONITORING_INTERVAL_SECONDS` | int | `900` | Evaluation cycle period (15 minutes default) |
| `DEMO_MODE` | bool | `True` | In demo mode, background thread is dormant to preserve deterministic demo state unless explicitly triggered |

---

## Scheduler Execution Lifecycle

```
[Timer Trigger / Manual Run Check]
               │
               ▼
   [Acquire Scheduler Lock]  ──(Locked)──► [Skip Cycle: CONCURRENT_RUN_IN_PROGRESS]
               │
               ▼
[Record Audit: MONITORING_CYCLE_STARTED]
               │
               ▼
    [Connector Health Check]
               │
               ▼
  [Fetch Recent Trusted Snapshots]
               │
               ▼
   [Execute SecurityDiffEngine]
               │
               ▼
   [Process NotificationEngine]
               │
               ▼
[Record Audit: MONITORING_CYCLE_COMPLETED]
               │
               ▼
     [Release Scheduler Lock]
```

---

## Safety & Security Guarantees

1. **Overlap Protection**: `threading.Lock` prevents simultaneous executions from running concurrently.
2. **Audit Logging**: Every cycle records `MONITORING_CYCLE_STARTED`, `MONITORING_CYCLE_COMPLETED`, or `MONITORING_CYCLE_FAILED` in the immutable `AuditEvent` log.
3. **No Secret Leakage**: Connector configurations are processed in memory; tokens and private keys are never written to logs or audit metadata.
4. **Idempotency**: Running two consecutive cycles without provider changes produces 0 new changes, 0 duplicate incidents, and 0 duplicate notifications.
