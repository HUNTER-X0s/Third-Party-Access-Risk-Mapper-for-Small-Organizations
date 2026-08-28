# ACCESSGUARD — API AUTHORIZATION MATRIX
# Endpoint Classification & Middleware Security Requirements

**Document Type:** Technical Specification  
**Version:** 4.0.0  
**Status:** Approved & Implemented  

---

## 1. Endpoint Classification Categories

Every API endpoint in AccessGuard is assigned to one of five security categories:

1. **`PUBLIC`**: Unauthenticated endpoint (e.g. `/health`, `/api/v1/auth/login`).
2. **`AUTHENTICATED`**: Any valid authenticated user session regardless of role (e.g. `/api/v1/auth/me`, `/api/v1/dashboard`).
3. **`ROLE_RESTRICTED`**: Requires specific role claims (e.g. `/api/v1/evidence` requires `SECURITY_ADMIN`, `AUDITOR`, or `SUPER_ADMIN`).
4. **`RESOURCE_RESTRICTED`**: Requires role claim AND object-level ownership check (BOLA/IDOR protection).
5. **`ADMIN_ONLY`**: Restricted strictly to `SUPER_ADMIN` or `SECURITY_ADMIN` (e.g. `/api/v1/users`, `/api/v1/demo/reset`).

---

## 2. API Endpoint Authorization Matrix

| Endpoint Route | Method | Classification | Required Roles | Tenant Scoped |
|---|---|---|---|---|
| `/health` | GET | `PUBLIC` | None | No |
| `/api/v1/auth/login` | POST | `PUBLIC` | None | Rate Limited |
| `/api/v1/auth/logout` | POST | `AUTHENTICATED` | Any Active User | Yes |
| `/api/v1/auth/me` | GET | `AUTHENTICATED` | Any Active User | Yes |
| `/api/v1/dashboard` | GET | `AUTHENTICATED` | Any Active User | Yes |
| `/api/v1/applications` | GET | `AUTHENTICATED` | Any Active User | Yes |
| `/api/v1/applications/{id}` | GET | `RESOURCE_RESTRICTED` | App Owner / Admin / Auditor | Yes |
| `/api/v1/applications/{id}/permissions` | GET | `RESOURCE_RESTRICTED` | Admin / IT / Auditor / App Owner | Yes |
| `/api/v1/applications/{id}/data` | GET | `RESOURCE_RESTRICTED` | Admin / IT / Auditor / Data Owner | Yes |
| `/api/v1/applications/{id}/findings` | GET | `RESOURCE_RESTRICTED` | Admin / IT / Auditor / App Owner | Yes |
| `/api/v1/findings` | GET | `AUTHENTICATED` | Any Active User | Yes |
| `/api/v1/findings/{id}` | GET | `RESOURCE_RESTRICTED` | Admin / IT / Auditor / App Owner | Yes |
| `/api/v1/findings/{id}/simulate-remediation` | POST | `ROLE_RESTRICTED` | Admin / IT / App Owner | Yes |
| `/api/v1/findings/{id}/remediation-analysis` | GET | `ROLE_RESTRICTED` | Admin / IT / App Owner / Auditor | Yes |
| `/api/v1/evidence/{id}` | GET | `ROLE_RESTRICTED` | `SUPER_ADMIN`, `SECURITY_ADMIN`, `AUDITOR` | Yes |
| `/api/v1/evidence/{id}/verify` | GET | `ROLE_RESTRICTED` | `SUPER_ADMIN`, `SECURITY_ADMIN`, `AUDITOR` | Yes |
| `/api/v1/graph` | GET | `ROLE_RESTRICTED` | Admin / IT / Auditor | Yes |
| `/api/v1/graph/paths` | GET | `ROLE_RESTRICTED` | Admin / IT / Auditor | Yes |
| `/api/v1/graph/blast-radius/{id}` | GET | `ROLE_RESTRICTED` | Admin / IT / Auditor | Yes |
| `/api/v1/snapshots` | GET | `ROLE_RESTRICTED` | Admin / Auditor | Yes |
| `/api/v1/snapshots` | POST | `ADMIN_ONLY` | `SUPER_ADMIN`, `SECURITY_ADMIN` | Yes |
| `/api/v1/snapshots/{idA}/compare/{idB}` | GET | `ROLE_RESTRICTED` | Admin / Auditor | Yes |
| `/api/v1/demo/reset` | POST | `ADMIN_ONLY` | `SUPER_ADMIN`, `SECURITY_ADMIN` | Yes |
| `/api/v1/demo/report` | GET | `ROLE_RESTRICTED` | Admin / Auditor | Yes |
| `/api/v1/users` | GET / POST | `ADMIN_ONLY` | `SUPER_ADMIN`, `SECURITY_ADMIN` | Yes |
| `/api/v1/users/{id}/role` | PATCH | `ADMIN_ONLY` | `SUPER_ADMIN`, `SECURITY_ADMIN` | Yes |

---

*AccessGuard API Authorization Matrix v4.0.0 — Enforced via FastAPI dependencies.*
