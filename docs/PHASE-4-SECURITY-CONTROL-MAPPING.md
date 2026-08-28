# ACCESSGUARD — SECURITY CONTROL MAPPING (PHASE 4)
# OWASP ASVS & NIST SP 800-161 Security Control Alignment

**Document Type:** Security Standards Alignment & Control Mapping  
**Version:** 4.0.0  
**Status:** Approved & Implemented  

---

## 1. Overview

AccessGuard Phase 4 maps its identity, session management, RBAC, and tenant boundary controls against established industry standards.

> **Legal & Compliance Disclaimer:** AccessGuard aligns with NIST SP 800-161 and OWASP ASVS guidelines for architecture and design inspiration. AccessGuard does NOT claim formal certification or third-party audit verification.

---

## 2. Security Control Mapping Matrix

| Standard | Control ID | Control Description | AccessGuard Implementation | Test Verification | Status |
|---|---|---|---|---|---|
| **OWASP ASVS** | **V2.1.1** | Verify all password verification is server-side. | PBKDF2 / bcrypt password hashing in `app/core/security.py`. Never client-side. | `test_authentication.py` | ✅ IMPLEMENTED |
| **OWASP ASVS** | **V2.2.1** | Anti-enumeration: Generic authentication error messages. | `/api/v1/auth/login` returns "Invalid credentials" for both unknown user and wrong password. | `test_authentication.py` | ✅ IMPLEMENTED |
| **OWASP ASVS** | **V3.1.1** | Session tokens generated using cryptographically secure random source. | UUIDv4 session tokens + RS256/HS256 signed JWT tokens. | `test_sessions.py` | ✅ IMPLEMENTED |
| **OWASP ASVS** | **V3.3.1** | Logout revokes session server-side. | `/api/v1/auth/logout` sets `revoked_at` timestamp in `UserSession` table. | `test_sessions.py` | ✅ IMPLEMENTED |
| **OWASP ASVS** | **V4.1.1** | Access control enforced server-side. | Server-side dependency functions `get_current_user` & `require_role`. Frontend visibility is UX only. | `test_authorization.py` | ✅ IMPLEMENTED |
| **OWASP ASVS** | **V4.1.2** | Deny by default. | All protected routes deny access if no valid session token is provided. | `test_authorization.py` | ✅ IMPLEMENTED |
| **OWASP ASVS** | **V4.1.3** | Object-level authorization (BOLA/IDOR protection). | Resource endpoints verify `resource.organization_id == user.organization_id`. Returns 404 on mismatch. | `test_idor_bola.py` | ✅ IMPLEMENTED |
| **NIST SP 800-161** | **AC-2** | Account Management & Membership Isolation. | Multi-tenant schema with explicit `OrganizationMembership` and `organization_id` queries. | `test_tenant_authorization.py` | ✅ IMPLEMENTED |
| **NIST SP 800-161** | **AC-3** | Access Enforcement (Least Privilege). | 7 explicit roles (`SUPER_ADMIN` to `VIEWER`) mapped via `PHASE-4-ROLE-MATRIX.md`. | `test_rbac.py` | ✅ IMPLEMENTED |
| **NIST SP 800-161** | **AU-2** | Event Logging for Auth & Security Events. | `AuditEvent` model logs `login_success`, `login_failure`, `logout`, `role_change`, `authorization_denied`. | `test_audit_authorization.py` | ✅ IMPLEMENTED |

---

*AccessGuard Security Control Mapping v4.0.0 — Aligned with OWASP ASVS v4.0 & NIST SP 800-161.*
