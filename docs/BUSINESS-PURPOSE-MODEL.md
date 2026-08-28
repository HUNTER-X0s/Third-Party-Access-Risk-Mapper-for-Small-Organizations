# BUSINESS PURPOSE & LEAST-PRIVILEGE DOMAIN MODEL
# AccessGuard: Structured Business Purpose & Excess Access Determination

**Document Type:** Technical Model Specification  
**Version:** 1.0  
**Date:** 2026-08-13  
**Status:** Approved Security Architecture  

---

## 1. Core Principle: Structured Validation over Free Text

In Phase 0, business purpose was represented as a simple text string (`business_purpose: "Marketing"`). **This is a security flaw.** Free-text declarations cannot be deterministically evaluated for least-privilege violations. A user could write `"Full admin access needed for reporting"` and bypass excess permission detection.

### The Hardened Principle:
> **Business Purpose must be selected from a curated, versioned taxonomy of Business Purpose Templates, each linked to a pre-defined set of Required and Optional Canonical Permissions. Free-text description is stored ONLY as advisory context for human reviewers.**

---

## 2. Conceptual Chain

```
BUSINESS PURPOSE TEMPLATE
       │
       ├──► REQUIRED CANONICAL PERMISSIONS (Mandatory for operation)
       │
       └──► OPTIONAL CANONICAL PERMISSIONS (Justified under specific features)
               │
               ▼
   GRANTED PERMISSIONS (Observed via OAuth connector)
               │
               ▼
    EXCESS ACCESS COMPUTATION
  (Granted Permissions - Required - Optional = EXCESS PERMISSIONS)
               │
               ▼
      DETERMINISTIC RISK IMPACT (+F2 Factor Increase)
```

---

## 3. Data Schema & Entities

### 3.1 `BusinessPurposeCatalog`
A system-curated, versioned catalog of legitimate SaaS integration use cases.

```python
class BusinessPurposeCatalog(Base):
    id: UUID
    purpose_code: str               # "EMAIL_MARKETING_AUTOMATION"
    display_name: str               # "Email Marketing & Campaign Automation"
    category: Enum                  # MARKETING, HR, DEV_OPS, FINANCE, PRODUCTIVITY
    description: str
    version: str                    # "v1.2"
    is_active: bool
```

### 3.2 `BusinessPurposeRequirement`
Maps a Purpose to its allowed/required canonical permissions.

```python
class BusinessPurposeRequirement(Base):
    id: UUID
    purpose_id: UUID (FK -> BusinessPurposeCatalog)
    permission_id: UUID (FK -> CanonicalPermission)
    requirement_type: Enum         # MANDATORY, OPTIONAL
    justification_rationale: str   # "Required to read user list to sync campaign recipients"
```

### 3.3 `ApplicationInstancePurpose`
The organization-specific binding of an application instance to one or more approved purposes.

```python
class ApplicationInstancePurpose(Base):
    id: UUID
    application_instance_id: UUID (FK -> ApplicationInstance)
    purpose_id: UUID (FK -> BusinessPurposeCatalog)
    approved_by_user_id: UUID (FK -> User)
    approved_at: datetime
    custom_notes: Optional[str]    # Free text for audit notes (NOT evaluated for risk logic)
```

---

## 4. Excess Access Calculation Algorithm

The excess permission detector operates deterministically:

```python
def compute_excess_permissions(
    granted_permission_ids: Set[UUID],
    assigned_purpose_ids: List[UUID]
) -> ExcessAccessResult:
    
    if not assigned_purpose_ids:
        # NO PURPOSE DECLARED: All permissions treated as UNJUSTIFIED (F2 Factor = 1.0)
        return ExcessAccessResult(
            excess_permissions=granted_permission_ids,
            is_unjustified_entirely=True,
            excess_ratio=1.0
        )
    
    # 1. Aggregate all allowed permission IDs (Mandatory + Optional) across all assigned purposes
    allowed_permission_ids = set()
    for purpose_id in assigned_purpose_ids:
        reqs = get_requirements_for_purpose(purpose_id)
        for r in reqs:
            allowed_permission_ids.add(r.permission_id)
            
    # 2. Identify Excess Permissions (Granted - Allowed)
    excess_permission_ids = granted_permission_ids - allowed_permission_ids
    
    # 3. Calculate Ratio
    total_granted = len(granted_permission_ids)
    excess_count = len(excess_permission_ids)
    ratio = (excess_count / total_granted) if total_granted > 0 else 0.0
    
    return ExcessAccessResult(
        excess_permissions=excess_permission_ids,
        is_unjustified_entirely=False,
        excess_ratio=ratio
    )
```

---

## 5. Curated Purpose Catalog Seed Examples

| Purpose Code | Display Name | Mandatory Permissions | Optional Permissions |
|---|---|---|---|
| `EMAIL_CAMPAIGN_SEND` | Email Campaign Automation | `send_email` | `read_user_directory` |
| `CALENDAR_SCHEDULING` | Meeting Scheduling Assistant | `read_calendar`, `write_calendar` | `read_user_profile` |
| `DOC_SIGNATURE` | Digital Signature Processing | `read_files`, `write_files` | `send_email` |
| `CODE_CI_CD` | Continuous Integration Runner | `read_code`, `write_code_status` | `deploy_environment` |
| `CRM_SYNC` | Customer Contact Sync | `read_contacts`, `write_contacts` | `read_user_directory` |

*Any permission outside these defined sets triggers explicit `EXCESS_PERMISSION` findings.*

---

*Business Purpose Model v1.0 — Approved Security Specification.*
