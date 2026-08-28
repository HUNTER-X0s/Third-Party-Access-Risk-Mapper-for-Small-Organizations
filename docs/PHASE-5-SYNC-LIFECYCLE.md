# AccessGuard Phase 5 — Connector Sync Lifecycle & Health

## Lifecycle States

Every connector synchronization run transitions through a deterministic state machine:

```
                  ┌──────────────────────┐
                  │       STARTED        │
                  └──────────┬───────────┘
                             │
                  ┌──────────▼───────────┐
                  │    AUTHENTICATING    │
                  └──────────┬───────────┘
                             │
                  ┌──────────▼───────────┐
                  │      COLLECTING      │
                  └──────────┬───────────┘
                             │
                  ┌──────────▼───────────┐
                  │     NORMALIZING      │
                  └──────────┬───────────┘
                             │
                  ┌──────────▼───────────┐
                  │      ANALYZING       │
                  └──────────┬───────────┘
                             │
       ┌─────────────────────┴─────────────────────┐
       │                                           │
┌──────▼──────────────┐                 ┌──────────▼───────────┐
│  SNAPSHOT_CREATED   │                 │        FAILED        │
│    COMPLETED        │                 │ (Last Snapshot Keeps)│
└─────────────────────┘                 └──────────────────────┘
```

---

## Health Status Codes

| Status Code | Meaning | Operational Guidance |
|---|---|---|
| **`HEALTHY`** | Sync completed successfully within threshold | Data is fresh; risk scores are live |
| **`DEGRADED`** | Partial collection failure (e.g. 1 repo failed) | Existing snapshot retained; warning logged |
| **`STALE`** | Data freshness > 1 hour (`3600s`) | Display banner: "Last trusted snapshot: X min ago" |
| **`AUTH_FAILED`** | App JWT signature rejected or revoked | Re-verify `GITHUB_APP_ID` & `GITHUB_PRIVATE_KEY` env vars |
| **`RATE_LIMITED`** | GitHub 429 / 403 rate limit hit | Halted collection; auto-resumes at `rate_limit_reset_at` |
| **`UNAVAILABLE`** | Provider unreachable (network/timeout) | System continues operating using last trusted state |
| **`MISCONFIGURED`** | Required environment variables missing | Configure credentials on server |

---

## Failure Isolation Invariants

- A complete failure of the GitHub provider API does **NOT** crash AccessGuard.
- Existing database records, authenticated user sessions, risk findings, and dashboard widgets remain 100% operational.
- The UI explicitly tags data staleness rather than displaying zero apps or crashing.
