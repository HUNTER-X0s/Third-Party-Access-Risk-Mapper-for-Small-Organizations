# ACCESSGUARD — ROLE-BASED ACCESS CONTROL (RBAC) MATRIX
# Phase 4 Role Definitions & Resource Authorization Matrix

**Document Type:** Technical Specification  
**Version:** 4.0.0  
**Status:** Approved & Implemented  

---

## 1. Role Definitions

AccessGuard defines 7 explicit operational roles under the principle of least privilege:

1. **`SUPER_ADMIN`**: Platform & organization super-administrator. Full administrative privileges over organization settings, user membership, and demo management.
2. **`SECURITY_ADMIN`**: Security operations lead. Full visibility over risk posture, attack graphs, evidence, findings, snapshot comparisons, remediation simulation, and report generation.
3. **`IT_ADMIN`**: Infrastructure administrator. Manages monitored applications, vendor inventory, and integration setup.
4. **`AUDITOR`**: Compliance auditor. Read-only access to posture scores, findings, verified evidence, security snapshots, and audit logs. Cannot modify users or execute remediations.
5. **`APP_OWNER`**: Business application owner. Can inspect assigned applications, permissions, and simulate remediation for their own integrations. Cannot view raw organization-wide evidence or manage users.
6. **`DATA_OWNER`**: Information security & data privacy officer. Inspects classified data assets, crown jewel reachability, and sensitivity levels.
7. **`VIEWER`**: Read-only stakeholder. Inspects high-level dashboard posture summaries. Cannot view raw payload evidence, export reports, or modify state.

---

## 2. Resource × Action Authorization Matrix

| Resource | Action | SUPER_ADMIN | SECURITY_ADMIN | IT_ADMIN | AUDITOR | APP_OWNER | DATA_OWNER | VIEWER |
|---|---|---|---|---|---|---|---|---|
| **Dashboard** | VIEW | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Applications** | VIEW | ✅ | ✅ | ✅ | ✅ | ✅ (Own) | ❌ | ✅ |
| **Permissions** | VIEW | ✅ | ✅ | ✅ | ✅ | ✅ (Own) | ❌ | ❌ |
| **Data Assets** | VIEW | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ |
| **Crown Jewels** | VIEW | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ |
| **Findings** | VIEW | ✅ | ✅ | ✅ | ✅ | ✅ (Own) | ❌ | ✅ |
| **Evidence Metadata** | VIEW | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Raw Evidence Payload** | VIEW | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Access Graph** | VIEW | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Attack Paths** | VIEW | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Blast Radius** | VIEW | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Remediation Simulation** | SIMULATE | ✅ | ✅ | ✅ | ❌ | ✅ (Own) | ❌ | ❌ |
| **Snapshots** | CREATE / COMPARE | ✅ | ✅ | ❌ | ✅ (View) | ❌ | ❌ | ❌ |
| **Reports** | EXPORT | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Audit Logs** | VIEW | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **User Management** | ADMINISTER | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Demo Reset** | RESET | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 3. Server-Side Enforcement Rules

- **Frontend Visibility is UX Only:** Hiding a button on the UI does not grant security. Every API endpoint validates `current_user.role` against the matrix.
- **Fail Closed:** If a role is unrecognized or missing from an endpoint's allowed list, the server returns `403 Forbidden`.
- **Object Ownership Checks:** An `APP_OWNER` user can only view findings and permissions for applications where `application.authorized_by_email == current_user.email`.

---

*AccessGuard Role Matrix v4.0.0 — Enforced in `backend/app/api/deps.py`.*
