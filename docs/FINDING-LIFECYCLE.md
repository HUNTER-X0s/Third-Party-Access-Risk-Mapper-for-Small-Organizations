# FINDING & REMEDIATION LIFECYCLE SPECIFICATION
# AccessGuard: Operational State Machine, Audit Hooks & Simulation Isolation

**Document Type:** Technical Specification  
**Version:** 1.0  
**Date:** 2026-08-13  
**Status:** Approved Security Architecture  

---

## 1. Finding Lifecycle State Machine

Every identified risk finding (e.g. `EXCESS_PERMISSION`, `SHADOW_APP`, `STALE_AUTHORIZATION`) transitions through a formal 8-state deterministic state machine.

```
                  ┌──────────────┐
                  │     NEW      │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │   TRIAGED    │
                  └──────┬───────┘
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
┌──────────────────┐           ┌──────────────────┐
│   ACKNOWLEDGED   │           │ RISK_ACCEPTED    │
└─────────┬────────┘           └──────────────────┘
          │
          ▼
┌──────────────────┐
│REMEDIATION_PLANNED│
└─────────┬────────┘
          │
          ▼
┌──────────────────┐
│APPROVAL_REQUIRED │
└─────────┬────────┘
          │
          ▼
┌──────────────────────┐
│REMEDIATION_IN_PROGRESS│
└─────────┬────────────┘
          │
          ▼
┌──────────────────┐
│    VERIFIED      │
└─────────┬────────┘
          │
          ▼
┌──────────────────┐
│      CLOSED      │
└──────────────────┘
```

---

## 2. State Transition Governance & Audit Rules

| State | Allowed Transitions | Permitted Roles | Required Audit Metadata |
|---|---|---|---|
| `NEW` | `TRIAGED` | System / Analyst / Admin | `detected_at`, `evidence_id`, `risk_engine_version` |
| `TRIAGED` | `ACKNOWLEDGED`, `RISK_ACCEPTED` | Analyst / Admin | `assigned_user_id`, `triage_notes` |
| `ACKNOWLEDGED` | `REMEDIATION_PLANNED` | Analyst / Admin | `target_sla_date` |
| `RISK_ACCEPTED` | `NEW` (if scope changes) | Owner / Admin ONLY | `justification_reason`, `expiration_date` |
| `REMEDIATION_PLANNED` | `APPROVAL_REQUIRED` | Analyst / Admin | `proposed_action_type`, `simulated_score_delta` |
| `APPROVAL_REQUIRED` | `REMEDIATION_IN_PROGRESS` | Admin / Owner | `approver_user_id`, `approval_timestamp` |
| `REMEDIATION_IN_PROGRESS` | `VERIFIED` | System Sync / Admin | `pre_remediation_evidence_hash`, `execution_timestamp` |
| `VERIFIED` | `CLOSED` | System / Admin | `post_remediation_evidence_hash`, `recalculated_score` |
| `CLOSED` | `NEW` (Reopening) | System Sync | `reopen_reason` (Scope re-detected on sync) |

---

## 3. Strict Separation of Simulation vs Execution

To prevent user confusion or false operational claims:

1. **Simulation Mode ("What-If Simulation")**:
   - Executes strictly in memory on server or client.
   - Calculates `simulated_score` and `risk_reduction_delta`.
   - **UI Requirement**: Rendered with a prominent Amber banner: `⚡ SIMULATION ONLY — NO PROVIDER CHANGES EXECUTED`.
   - Does NOT alter database finding state.

2. **Real Execution Mode**:
   - Triggers OAuth API revocation or provider admin webhooks (where connectors exist).
   - Generates an immutable `AuditEvent` (`ACTION: REMEDIATION_EXECUTION`).
   - Requires subsequent connector sync to achieve `VERIFIED` state.

---

## 4. Reopening Behavior (Continuous Assurance)

If an administrator marks a finding as `CLOSED` or `RISK_ACCEPTED`, but a subsequent connector synchronization detects that the third-party application still retains the excess permission (or the user re-authorizes the scope):

- The state machine immediately **REOPENS** the finding (`CLOSED -> NEW`).
- An immutable `AuditEvent` (`TYPE: FINDING_REOPENED_SECURITY_REGRESSION`) is emitted.
- Security posture trend charts record a security regression event.

---

*Finding Lifecycle Specification v1.0 — Approved Security Architecture.*
