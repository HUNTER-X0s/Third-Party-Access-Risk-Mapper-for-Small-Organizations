# Security Diff Model — Change Detection Specification

## Overview
The `SecurityDiffEngine` is a deterministic change-detection engine comparing two `SecuritySnapshot` objects using stable identifiers. It never uses AI to determine what changed.

## Change Taxonomy

| Change Type | Object Type | Trigger Condition |
|---|---|---|
| `APPLICATION_ADDED` | APPLICATION | New app in current snapshot not in baseline |
| `APPLICATION_REMOVED` | APPLICATION | App in baseline not in current snapshot |
| `SHADOW_SAAS_DETECTED` | APPLICATION | New app observed with no approved `ApplicationBaseline` |
| `PERMISSION_ESCALATED` | PERMISSION | New excess scope not in baseline `excess_scopes` |
| `PERMISSION_REDUCED` | PERMISSION | Excess scope present in baseline but not in current |
| `CROWN_JEWEL_REACHABILITY_CREATED` | DATA_ASSET | App gains direct/admin access to a Crown Jewel asset |
| `CROWN_JEWEL_REACHABILITY_REMOVED` | DATA_ASSET | App loses direct access to Crown Jewel asset |
| `RISK_INCREASED` | ORGANIZATION | `risk_after - risk_before > 0.1` |
| `RISK_DECREASED` | ORGANIZATION | `risk_after - risk_before < -0.1` |
| `FINDING_CREATED` | FINDING | Finding ID in current not in baseline manifest |
| `FINDING_RESOLVED` | FINDING | Finding ID in baseline manifest not in current |

## Change Significance Levels

| Severity | Criteria |
|---|---|
| **Critical** | ADMIN permission escalation, crown-jewel reachability, risk delta > 15 |
| **High** | WRITE permission escalation, risk delta > 5, Shadow SaaS with sensitive data |
| **Medium** | New application with moderate risk |
| **Low** | READ permission added, benign application added |
| **Info** | Permission reduced, finding resolved, application removed |

## Stable Comparison Identifiers

Entities are compared using:
- **Applications**: `ApplicationInstance.id` (internal UUID, stable across syncs)
- **Permissions**: Canonical scope string (e.g., `organization_admin`, `repo_write`)
- **Findings**: `RiskFinding.id` (deterministic UUID)
- **Snapshots**: `SecuritySnapshot.id`

Row ordering is never used as a comparison key.

## Determinism Guarantee

Running `SecurityDiffEngine.compare_snapshots(snap_a.id, snap_b.id)` twice with the same inputs produces identical `SecurityChange` records. Change identity is derived from canonical entity identifiers, not timestamps or session state.

## Change Confidence

| Confidence | Condition |
|---|---|
| `VERIFIED` | Both snapshots are complete trusted snapshots from a successful connector sync |
| `HIGH` | One snapshot is inferred or partially derived |
| `MEDIUM` | Stale connector data with known gaps |
| `LOW` | Inferred change with incomplete evidence |
