# 06 — Security Principles
# AccessGuard: Platform Security Model

**Document Type:** Security Principles — Phase 0  
**Version:** 1.0  
**Date:** 2026-08-13  

---

## Preamble

A security intelligence platform must itself be exemplary in its security posture. Any vulnerability in AccessGuard represents an ironic and critical failure: an attacker who compromises the platform gains visibility into an organization's entire third-party access landscape, enabling them to choose the highest-value attack path.

This document defines the security principles, controls, and threat model for the AccessGuard platform itself.

---

## Threat Model Summary

### Assets to Protect

| Asset | Value to Attacker |
|---|---|
| Application inventory | Reveals what integrations exist; enables targeted attacks |
| Permission grants | Shows what each app can access; enables crafted exploits |
| OAuth tokens/credentials | Direct access to organizational resources |
| Risk findings | Roadmap of unpatched vulnerabilities |
| Audit logs | Evidence trail; tampering enables cover-up |
| AI conversation context | May contain sensitive organizational data |
| User accounts | Lateral movement within AccessGuard |

### High-Risk Trust Boundaries

| Boundary | Risk | Control |
|---|---|---|
| Browser → API | Untrusted user input; session attacks | JWT validation, CSRF tokens, input validation |
| API → Database | Injection; tenant leakage | Parameterized queries, ORM, tenant filters |
| Connector → External Provider | Malicious API responses | Response validation, sandbox execution |
| External data → Display | XSS via third-party metadata | Output encoding, Content Security Policy |
| AI layer ← External data | Prompt injection | Server-controlled prompts, sanitized context |
| Admin actions | Privilege abuse | RBAC, audit logging, approval workflows |

---

## Authentication

### Principles
- Every access to AccessGuard requires authentication
- Authentication uses JWT (RS256) with short-lived access tokens
- Refresh tokens use rotation (old token invalidated on use)
- Multi-factor authentication is strongly encouraged and trackable

### Implementation Requirements
- Access tokens: 15-minute expiry
- Refresh tokens: 7-day expiry, rotation on every use
- Tokens stored in HttpOnly, Secure, SameSite=Strict cookies (not localStorage)
- Failed authentication attempts are rate-limited and logged
- Token revocation list maintained for logout/session invalidation
- Passwords hashed with Argon2id (not MD5, SHA-1, or bcrypt with weak cost factor)

### OAuth for AccessGuard's Own Auth
- Organizations may authenticate via Google OAuth 2.0 or Microsoft OAuth
- PKCE required for all OAuth flows (RFC 9700 compliant)
- Implicit Grant explicitly forbidden
- State parameter validated to prevent CSRF in OAuth callback

---

## Authorization (RBAC)

### Roles

| Role | Description |
|---|---|
| **Owner** | Full access; manages org settings and billing |
| **Admin** | Full security access; cannot change billing |
| **Analyst** | Read access + risk analysis; cannot remediate |
| **Viewer** | Read-only; cannot see full permission details |

### Principles
- Authorization is enforced server-side on every API endpoint
- No security decision is made based on client-supplied role claims alone
- Role is always verified against the database for the authenticated user's organization
- The Authorization header is verified; the role within it is not trusted without DB lookup
- Least-privilege by default: new users are assigned Viewer role

### Resource-Level Authorization
- Every API endpoint that accesses a resource verifies:
  1. User is authenticated
  2. User's organization matches the resource's organization_id
  3. User's role permits the requested action on this resource type

---

## Tenant Isolation

This is the single most critical security control in a multi-tenant system.

### Database Layer
- Every table that stores organizational data includes `organization_id`
- Every query includes `WHERE organization_id = :current_org_id`
- PostgreSQL Row-Level Security (RLS) policies enforce this at the database layer (defense-in-depth)
- No query may use `SELECT *` from a tenant-scoped table without the organization filter

### Application Layer
- A `TenantContext` object is established at authentication and passed through all service calls
- Services MUST receive TenantContext as an explicit parameter — never infer it from global state
- Integration tests verify that Org A's resources are never returned to Org B's authenticated user

### Testing Requirement
- Tenant isolation MUST be covered by explicit cross-tenant access attempt tests
- Tests simulate: "as an Org B user, request Org A's ApplicationInstance" → expect 403 or 404

---

## Input Validation

### Principle: All input is untrusted

This applies to:
- Browser form submissions
- API request bodies
- API path parameters and query strings
- Data returned from third-party OAuth provider APIs
- Application metadata (names, descriptions) from external sources
- Webhook payloads from external services
- AI model outputs

### Implementation
- Pydantic v2 schemas validate ALL request bodies at the API layer
- Strict type validation — extra fields are rejected (`.model_config = ConfigDict(extra="forbid")`)
- String length limits enforced on all text fields
- Enum validation for all categorical fields
- Path traversal prevented (no file paths accepted from user input)
- SSRF prevention: URL inputs are validated against an allowlist of permitted domains

---

## Output Encoding & XSS Prevention

- All data rendered in the React frontend is treated as untrusted
- React's JSX escapes text content by default — `dangerouslySetInnerHTML` is forbidden
- Content Security Policy (CSP) header with strict directive set
- Application names, vendor names, permission descriptions from external APIs are sanitized via DOMPurify before any display

---

## SQL Injection Prevention

- SQLAlchemy ORM with parameterized queries for all database operations
- Raw SQL is forbidden except in specifically reviewed migration scripts
- No user-controlled values are interpolated into SQL strings

---

## CSRF Protection

- All state-changing API endpoints (POST, PUT, PATCH, DELETE) use CSRF tokens
- Tokens stored in session; verified on each state-changing request
- SameSite=Strict cookie attribute provides additional CSRF protection

---

## Session Security

- HttpOnly cookies prevent JavaScript access to tokens
- Secure flag ensures cookies only sent over HTTPS
- SameSite=Strict prevents cross-origin cookie submission
- Session invalidation on logout (refresh token revoked)
- Concurrent session limits (configurable; default: 3 active sessions)

---

## SSRF Prevention

Connectors that fetch data from external URLs must:
- Validate all URLs against an allowlist of provider domains
- Reject private IP ranges (10.x, 172.16.x, 192.168.x, 127.x, ::1)
- Use a separate network segment for connector execution (production target)
- Never follow redirect chains beyond 3 hops

---

## API Security

- Rate limiting on all endpoints (configurable by role and endpoint sensitivity)
- Specific rate limits:
  - Authentication: 5 attempts per 60 seconds per IP
  - API general: 200 requests per minute per authenticated user
  - AI analyst: 10 requests per minute per user (cost + abuse prevention)
- API versioning: all endpoints prefixed with `/api/v1/`
- OpenAPI schema validates request and response shapes
- HTTP methods strictly enforced (no method override tricks)

---

## Secrets Management

- No secrets in source code (enforced by pre-commit hooks checking for common patterns)
- No secrets in Docker images
- Secrets loaded from environment variables at runtime
- In production: secrets manager (AWS Secrets Manager, GCP Secret Manager, or HashiCorp Vault)
- Google Gemini API key never exposed to frontend
- OAuth provider credentials (for connectors) stored encrypted in the database; referenced by ID

---

## AI Layer Security

The AI layer introduces specific security challenges:

### Prompt Injection
- AI prompts are constructed entirely on the server side
- User input is never directly concatenated into prompts
- Third-party data (app names, descriptions) included in AI context is sanitized before injection
- A malicious application named `'; DROP TABLE applications; --` must not affect the AI prompt or any query

### Data Leakage
- AI context is scoped to the authenticated organization only
- No cross-tenant data is ever included in AI context
- AI responses are logged for audit purposes (sanitized)
- The AI model does not receive raw credentials or tokens — only derived metadata

### AI Trust Boundary
- AI output is returned to the UI with a clear "AI Suggestion" label
- AI output is never written to the database as authoritative data
- AI output never modifies risk scores, policies, or remediation statuses
- AI output is sanitized before display (HTML stripped, markdown rendered safely)

---

## Audit Logging

### What is logged
- All authentication events (success, failure, logout)
- All authorization failures (403 responses)
- All data creation, modification, and deletion events
- All remediation actions (proposed, approved, rejected, executed)
- All report generation events
- All policy changes
- All admin actions

### Audit Log Security
- Audit events are append-only (no UPDATE, no DELETE on the audit_events table)
- Audit events include: timestamp, user_id, org_id, action, resource, outcome, IP (anonymized)
- Audit log access is restricted to Admin and Owner roles
- Audit logs are retained per organization's configured retention period

---

## Encryption

### In Transit
- All external communication over TLS 1.2+ (TLS 1.3 preferred)
- HTTP Strict Transport Security (HSTS) header
- TLS termination at nginx

### At Rest
- Database encryption at the storage level (cloud provider disk encryption)
- Sensitive fields (OAuth credentials, API keys) encrypted at the application level using AES-256-GCM before storage
- Encryption keys stored separately from encrypted data

---

## Dependency Security

- All Python dependencies pinned to exact versions in `requirements.txt`
- All NPM dependencies pinned in `package-lock.json`
- `pip-audit` and `npm audit` run in CI pipeline
- Dependabot or equivalent configured for automated dependency vulnerability alerts
- No dependency added without security review (check for CVEs, maintenance status)

---

## Secure Deployment

- Docker images built from minimal base images (python:3.12-slim)
- No root processes inside containers
- Read-only filesystem where possible
- Environment variables for all configuration; no config files with secrets
- `.env` files in `.gitignore`; `.env.example` with placeholder values committed
- Container image scanning in CI pipeline

---

## Security Testing Requirements

The following security tests are required before any release:

1. **Authentication bypass** — Attempt to access protected endpoints without valid JWT
2. **Authorization bypass** — Attempt to access another organization's resources
3. **Input validation** — Submit malformed, oversized, and injection-attempt payloads
4. **Tenant isolation** — Verify cross-tenant access returns 403/404
5. **CSRF** — Verify state-changing requests require CSRF tokens
6. **Rate limiting** — Verify rate limits are enforced
7. **XSS** — Verify external data does not render as HTML
8. **Audit log completeness** — Verify all required events are logged

---

## Standards Referenced

| Standard | Application to AccessGuard |
|---|---|
| NIST SP 800-207 (Zero Trust) | Least-privilege, never trust client-supplied identity |
| OWASP Top 10 Web (2021) | XSS, injection, broken auth, broken access control prevention |
| OWASP API Security Top 10 (2023) | BOLA prevention, broken auth, SSRF prevention |
| IETF RFC 9700 (OAuth 2.0 BCP) | PKCE, short-lived tokens, token storage |
| CIS Controls v8, Control 2 | Software asset management (of AccessGuard's own dependencies) |
| NIST SP 800-63B | Password and authenticator assurance |

---

*Security principles version 1.0 — These are requirements, not aspirations.*
