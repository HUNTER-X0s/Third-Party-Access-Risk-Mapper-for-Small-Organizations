# AccessGuard Phase 9: Trust-Boundary & Input-Trust Audit

**Date:** 2026-08-14  
**Audit Scope:** End-to-End Trust Boundaries, Data Ingestion, Privilege Escalation Vectors, and Sanitization

---

## 1. Architectural Trust-Boundary Flow

```
[ BROWSER CLIENT ]
       │
       ▼  (Untrusted Network / Public Client)
[ FRONTEND UI (React / TS) ]
       │  • Form inputs, URL params, JWT cookies
       │  • Strictly client-side presentation
       ▼
═════════════════════════════ TRUST BOUNDARY 1 ═════════════════════════════
[ API GATEWAY / SECURITY MIDDLEWARE ]
       │  • CORS origin validation & SameSite cookie validation
       │  • Double-defense CSRF (Origin header + X-Requested-With)
       │  • Pydantic schema validation & sanitization
       │  • JWT signature & issuer verification (RS256 / HS256)
       │  • Session revocation check against database UserSession table
       ▼
═════════════════════════════ TRUST BOUNDARY 2 ═════════════════════════════
[ SERVER-SIDE AUTHORIZATION (RBAC / ABAC) ]
       │  • DB-backed role verification (SUPER_ADMIN, SECURITY_ADMIN, etc.)
       │  • Mandatory organization_id query scoping on every ORM query
       │  • BOLA / IDOR protection (Object ownership verification)
       ▼
[ APPLICATION ENGINES & SERVICES ]
  ┌───────────────────────┬────────────────────────┬───────────────────────┐
  │ RiskEngine v1.5.0     │ GraphEngine            │ BlastRadiusCalculator │
  │ (Deterministic CPU)   │ (Traversals)           │ (Reachability)        │
  ├───────────────────────┼────────────────────────┼───────────────────────┤
  │ SupplierRiskEngine    │ RemediationOptimizer   │ SnapshotEngine        │
  │ (NIST SP 1326)        │ (Simulation Only)      │ (Diffs & Changes)     │
  └───────────────────────┴────────────────────────┴───────────────────────┘
       │                                                   │
       ▼                                                   ▼
═══════════ TRUST BOUNDARY 3 ═══════════   ═══════════ TRUST BOUNDARY 4 ═══════════
[ DATABASE (PostgreSQL / SQLite) ]         [ EXTERNAL SERVICE BOUNDARIES ]
  • Row-level tenant isolation               ├── Live SaaS Providers (GitHub)
  • Encrypted sensitive configs              │   • Architectural Read Guard (READ=True, WRITE=False)
  • Append-only evidence & audit logs        │   • Secret Redaction ([REDACTED]) in raw payloads
                                             └── AI Provider (Google Gemini)
                                                 • Advisory only; zero execution privileges
                                                 • <UNTRUSTED_SECURITY_DATA> delimiter bounding
```

---

## 2. Input Classification & Sanitization Matrix

| Data Source | Trust Level | Ingestion Handling | Sanitization / Defense |
|---|---|---|---|
| **User Request Body** | Untrusted | Pydantic V2 schema validation | Strict typing, regex format constraints, field length limits |
| **Session Cookie / Bearer Token** | Untrusted until verified | Cryptographic JWT decode + DB session revocation lookup | Signature verification, issuer matching, revocation check |
| **Provider API Responses (GitHub)** | Untrusted | Normalization pipeline | Secret key stripping (`redact_secrets()`), conservative unknown permission mapping |
| **Supplier Metadata & Notes** | Untrusted | AI Context Builder | Wrapped in `<UNTRUSTED_SECURITY_DATA>` delimiter tags to prevent prompt injection |
| **AI Generated Responses** | Advisory Only | Citation Validator | Verified against grounded security fact IDs before rendering |
| **Database State** | Trusted within Tenant | ORM Query Scoping | Automatic `filter(Model.organization_id == org_id)` |
