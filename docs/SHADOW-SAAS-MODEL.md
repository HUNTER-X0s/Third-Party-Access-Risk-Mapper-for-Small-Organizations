# Shadow SaaS Model

## Definition

**Shadow SaaS** = An application observed in active use within an organization that does NOT have an approved `ApplicationBaseline` record.

## Detection Logic

```
Application observed (live connector / imported snapshot)
    ↓
ApplicationBaseline lookup (organization_id + application_instance_id)
    ↓
is_approved == False OR no baseline record
    ↓
Shadow SaaS Detected
    ↓
SecurityChange: SHADOW_SAAS_DETECTED
```

## Shadow SaaS Severity Matrix

| Condition | Severity |
|---|---|
| Unknown app + no sensitive data | Low |
| Unknown app + internal data | Medium |
| Unknown app + customer PII | High |
| Unknown app + EXPORT permission | High |
| Unknown app + Crown Jewel access | Critical |
| Unknown app + ADMIN + Crown Jewel | Critical |

## ApplicationBaseline Fields

```python
class ApplicationBaseline:
    application_instance_id: str       # Links to ApplicationInstance
    approved_permissions: list[str]    # Canonical permission strings
    approved_data_categories: list[str]
    is_approved: bool
    approval_status: str               # APPROVED, UNAPPROVED, REVIEW_REQUIRED, RESTRICTED, REJECTED
    approved_by_user_id: str | None    # SECURITY_ADMIN who approved
    approved_at: datetime | None
    first_seen_at: datetime            # First connector observation
    last_seen_at: datetime             # Most recent observation
```

## Shadow SaaS Lifecycle

```
FIRST_SEEN (SHADOW_SAAS_DETECTED alert)
    ↓
REVIEW_REQUIRED
    ↓ (SECURITY_ADMIN decision)
    ├── APPROVED → Monitor with baseline
    ├── RESTRICTED → Monitor with limited scope
    └── REJECTED → Remove from access
```

## Phase 7 Demo Scenario

**App**: "Unknown AI Productivity Tool"  
**Vendor**: AI Productivity Inc. (SOC 2: None, Trust Score: 15)  
**Permissions**: `EXPORT` (data_export_all) — excess  
**Data Exposure**: Customer PII Database  
**Risk Score**: 78.0 (High)  
**Approval Status**: REVIEW_REQUIRED  

Correct finding generated: `SHADOW SaaS: Unapproved AI Tool Exporting Customer PII`  
Severity: **High**

## Governance Rules

1. Shadow SaaS detection is **read-only** — no automatic access revocation.
2. Dismissal/approval requires `SECURITY_ADMIN` or `SUPER_ADMIN` role.
3. Evidence of first/last seen is preserved even after approval.
4. All approval actions are written to the `AuditEvent` log.
