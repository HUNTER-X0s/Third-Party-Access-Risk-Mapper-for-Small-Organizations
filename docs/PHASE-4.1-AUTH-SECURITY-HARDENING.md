# ACCESSGUARD — PHASE 4.1 SECURITY HARDENING SPECIFICATION
# Authentication, Cookie Transport, Session Revocation & Audit Verification

**Document Type:** Security Specification & Hardening Architecture  
**Version:** 4.1.0  
**Date:** 2026-08-13  
**Status:** Approved & Active Implementation  

---

## 1. Executive Summary

Phase 4.1 hardens AccessGuard's identity and authorization boundary against session theft, session replay, privilege escalation, cross-site request forgery (CSRF), and credential abuse.

This phase introduces:
- **HttpOnly Cookie Transport:** Primary JWT session transport via `HttpOnly`, `SameSite=Lax`, `Secure` (production) cookies.
- **Database-Backed Session Revocation:** Instant session invalidation on logout, suspension, or role change.
- **Login Abuse Protection:** Exponential lockout after 5 consecutive failed attempts.
- **Strict JWT Cryptographic Claims:** Enforced `HS256`/`RS256` signature verification, issuer check, and expiration validation.
- **Audit Compliance:** Comprehensive logging for all identity and authorization state mutations.

---

## 2. Token Transport Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    BROWSER CLIENT                       │
│  - HttpOnly Cookie: access_token (No JS access)        │
│  - X-CSRF-Token / X-Requested-With header              │
└────────────────────────────┬────────────────────────────┘
                             │ HTTPS (Credentials Included)
┌────────────────────────────▼────────────────────────────┐
│                  FASTAPI API GATEWAY                    │
│  1. Extract Cookie 'access_token' or 'Bearer' header    │
│  2. Validate JWT Signature (HS256/RS256) & Issuer       │
│  3. Verify DB UserSession active & unrevoked            │
│  4. Verify DB User status == ACTIVE                     │
│  5. Scope Organization Query to user.organization_id    │
└─────────────────────────────────────────────────────────┘
```

### 2.1 Transport Methods Supported
1. **`HttpOnly` Cookie (Primary Web Client):** Set via `Set-Cookie: access_token=<jwt>; HttpOnly; SameSite=Lax; Path=/api/v1`. Prevents XSS script token theft.
2. **`Authorization: Bearer <jwt>` Header (API & SDK Clients):** Supported for headless automated scripts and integration tests.

---

## 3. Login Throttling & Anti-Enumeration Policy

| Metric | Threshold / Policy | Operational Action |
|---|---|---|
| Max Failed Attempts | 5 consecutive failures | Account status set to `LOCKED` for 15 minutes (`locked_until`). |
| Error Message | "Invalid email or password" | Identical error returned for non-existent users, wrong passwords, and locked accounts to prevent username enumeration. |
| Reset Criteria | Successful authentication | `failed_login_count` reset to 0 upon valid login. |

---

## 4. Real-Time Authorization Validation (Post-Issuance)

JWT claims (`role`, `org_id`) are validated against live database records on **EVERY request**:
1. **User Suspension:** If `user.status != "ACTIVE"`, request returns `403 Forbidden` immediately.
2. **Role Downgrade:** If `user.role` was changed in DB after token issuance, backend enforces the **current database role**, NOT the stale JWT claim.
3. **Session Revocation:** Logout sets `UserSession.revoked_at`. Replay of the token returns `401 Unauthorized`.

---

## 5. Security Control Mapping

- **OWASP ASVS V3.3.1:** Server-side session revocation.
- **OWASP ASVS V3.4.1:** Cookie HttpOnly flag enforced.
- **OWASP ASVS V4.1.3:** Object-level authorization (BOLA/IDOR).
- **NIST SP 800-161 AC-2:** User account lifecycle and membership isolation.

---

*AccessGuard Phase 4.1 Security Specification v4.1.0 — Authoritative.*
