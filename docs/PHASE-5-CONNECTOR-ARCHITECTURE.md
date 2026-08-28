# AccessGuard Phase 5 — Provider-Neutral Connector Architecture

## Executive Overview

Phase 5 introduces AccessGuard's provider-neutral connector architecture. The design allows AccessGuard to ingest live access, permission, and installation metadata from third-party SaaS applications (such as GitHub, Google Workspace, Microsoft 365, Slack) without altering the deterministic core security engines (`risk_engine_v1.5.0`, `GraphEngine`, `SnapshotEngine`).

---

## Architectural Principles & Invariants

1. **Deterministic Core Isolation**: Live provider data is normalized before crossing the domain boundary. Risk scores, excess permission detection, and graph relationships use the exact same deterministic formulas for live data as they do for demo data.
2. **Architectural Read Guard (`READ=True`, `WRITE=False`)**: In Phase 5, all provider connectors inherit from `BaseConnector` which enforces an architectural write guard. Any call to `revoke_permission`, `grant_permission`, or `delete_resource` raises `NotImplementedError`.
3. **Provider-Neutral Interface**: All connectors implement `BaseConnector`. Provider-specific response types (e.g. GitHub REST API objects) never escape the connector boundary. Only normalized canonical objects (`NormalizedInstallation`, `NormalizedRepository`, `NormalizedPermission`) cross into the domain layer.
4. **Secret Storage Boundary**: OAuth tokens, private key PEMs, and client secrets are strictly environment-managed (`GITHUB_APP_ID`, `GITHUB_PRIVATE_KEY`). Secrets are NEVER stored in database tables, logged to log files, or sent to frontend clients.
5. **Tamper-Evident Evidence Provenance**: Every external observation creates a `RawEvidence` record with secret fields redacted (`[REDACTED]`) and a SHA-256 integrity hash (`payload_hash_sha256`).
6. **Conservative Unknown Handling**: Unrecognized provider scopes are mapped to `CanonicalPermission.UNKNOWN` with `NormalizationStatus.UNKNOWN` and `HIGH` severity. They are surfaced for review rather than silently downgraded.

---

## Data Pipeline Diagram

```
┌─────────────────────────────────────────┐
│     EXTERNAL PROVIDER (e.g. GitHub API) │
└────────────────────┬────────────────────┘
                     │ HTTP GET (Bearer JWT / Installation Token)
┌────────────────────▼────────────────────┐
│          PROVIDER CONNECTOR             │
│   (RS256 Auth, Pagination, Rate-Limits) │
└────────────────────┬────────────────────┘
                     │ Raw JSON Payload
┌────────────────────▼────────────────────┐
│      NORMALIZATION & SECRET REDACTION   │
│   - Redact tokens/keys ([REDACTED])     │
│   - SHA-256 Evidence Hash               │
│   - Map scopes to Canonical Permissions │
└────────────────────┬────────────────────┘
                     │ Normalized Dataclasses
┌────────────────────▼────────────────────┐
│       SECURITY FACTS & DOMAIN MAPPER    │
│   - GITHUB_APP_INSTALLED SecurityFacts  │
│   - Vendor, Application, Instance       │
│   - PermissionGrant, AccessRelationship │
└────────────────────┬────────────────────┘
                     │ SQLAlchemy Domain Entities
┌────────────────────▼────────────────────┐
│     EXISTING DETERMINISTIC ENGINES      │
│   - Risk Engine v1.5.0                  │
│   - Graph Engine                        │
│   - Security Snapshot Engine            │
└─────────────────────────────────────────┘
```

---

## Supported & Future Connectors

| Provider | Status | Mode | Read Guard | Auth Method |
|---|---|---|---|---|
| **GitHub App** | ✅ Live Ready / Fully Tested | Live + Demo | `READ=True, WRITE=False` | RS256 App JWT + Ephemeral Installation Token |
| **Google Workspace** | 📋 Planned (Phase 6) | Architecture Ready | `READ=True, WRITE=False` | OAuth2 Service Account / Domain-Wide Delegation |
| **Microsoft 365** | 📋 Planned (Phase 6) | Architecture Ready | `READ=True, WRITE=False` | Azure AD App Registration (Graph API) |
| **Slack** | 📋 Planned (Phase 6) | Architecture Ready | `READ=True, WRITE=False` | Bot Token / User Token Scopes |
