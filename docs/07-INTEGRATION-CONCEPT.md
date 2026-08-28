# 07 — Integration Concept
# AccessGuard: Integration Architecture & Connector Framework

**Document Type:** Integration Concept — Phase 0  
**Version:** 1.0  
**Date:** 2026-08-13  
**Status:** Conceptual — Connector architecture defined; implementation begins Phase 1  

---

## Problem Statement for Integrations

The core value of AccessGuard depends on data quality. Three data acquisition modes exist:

1. **Manual entry** — Organization manually registers apps and permissions
2. **Seeded demo data** — High-quality realistic pre-loaded data for demonstration
3. **Live connectors** — Real-time data pulled from provider APIs

For the hackathon, modes 1 and 2 enable full demo capability. One live connector (Google Workspace) is the stretch goal for a real-world proof of concept.

---

## Connector Architecture (Provider-Neutral Framework)

### Design Principles

1. **Provider-neutral** — Core domain objects are independent of any provider's API format
2. **Isolated** — Each connector runs in a sandboxed context; failure in one connector does not affect others
3. **Normalized** — All connector output is normalized to the canonical Permission model before storage
4. **Untrusted** — All data from connectors is treated as potentially malicious external input
5. **Idempotent** — Running the same sync twice produces the same database state
6. **Auditable** — Every sync is logged with the data source, timestamp, and outcome

### Connector Interface (Abstract)

Every connector must implement this interface:

```python
class BaseConnector(ABC):
    """
    Abstract base class for all provider connectors.
    All methods receive the organization_id and return normalized domain objects.
    """
    
    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Identifies the provider (google_workspace, microsoft365, etc.)"""
        pass
    
    @abstractmethod
    async def validate_credentials(self, credentials: ConnectorCredentials) -> ValidationResult:
        """Verify credentials are valid before use. Never store raw credentials."""
        pass
    
    @abstractmethod
    async def discover_applications(self, org_id: UUID, credentials: ConnectorCredentials) -> List[ApplicationDiscoveryResult]:
        """
        Returns all third-party apps authorized within this provider.
        Output must be in canonical ApplicationDiscoveryResult format — 
        never return raw provider API responses.
        """
        pass
    
    @abstractmethod
    async def discover_permission_grants(self, org_id: UUID, app_id: str, credentials: ConnectorCredentials) -> List[PermissionGrantDiscoveryResult]:
        """Returns normalized permission grants for a specific application."""
        pass
    
    @abstractmethod
    async def get_authorization_history(self, org_id: UUID, credentials: ConnectorCredentials) -> List[AuthorizationEvent]:
        """Returns timestamped authorization changes where available from provider."""
        pass
```

### Normalized Discovery Output

Connector output must always use these canonical types before reaching the application layer:

```python
@dataclass
class ApplicationDiscoveryResult:
    """Provider-neutral representation of a discovered application."""
    raw_client_id: str               # Provider's identifier for the app
    canonical_name: str              # Normalized app name
    discovered_name: str             # Exact name from provider API
    publisher: str                   # App publisher/vendor
    is_verified: bool                # Provider-verified status
    authorization_type: str          # "oauth2", "api_key", "service_account"
    authorized_at: Optional[datetime]
    authorized_by_user_email: Optional[str]
    last_activity_at: Optional[datetime]
    raw_scopes: List[str]            # Provider-specific scope strings
    normalized_permissions: List[CanonicalPermission]  # After normalization

@dataclass
class CanonicalPermission:
    """A normalized permission, independent of provider format."""
    raw_scope: str                   # Original scope string
    canonical_id: str                # Maps to Permission.canonical_name
    display_name: str                # Human-readable name
    severity: PermissionSeverity     # critical/high/medium/low
    data_classifications: List[str]  # Data types this permission accesses
```

---

## Permission Normalization Engine

The normalization engine translates provider-specific OAuth scopes into canonical permissions.

### Normalization Table (Seed Data Required)

This table must be seeded for each supported provider. It is the foundation of cross-provider comparison.

```
ProviderScope Table (seeded, not user-generated):

Google Workspace Examples:
  https://www.googleapis.com/auth/gmail.readonly     → read_email          (severity: high)
  https://www.googleapis.com/auth/gmail.send         → send_email          (severity: high)
  https://www.googleapis.com/auth/drive.readonly     → read_files          (severity: medium)
  https://www.googleapis.com/auth/drive              → read_write_files    (severity: high)
  https://www.googleapis.com/auth/admin.directory.user.readonly → read_user_directory (severity: high)
  https://www.googleapis.com/auth/calendar.readonly  → read_calendar       (severity: low)
  https://www.googleapis.com/auth/contacts.readonly  → read_contacts       (severity: medium)

Microsoft 365 Examples:
  Mail.Read          → read_email          (severity: high)
  Mail.Send          → send_email          (severity: high)
  Files.Read.All     → read_files          (severity: medium)
  Files.ReadWrite.All → read_write_files   (severity: high)
  User.Read.All      → read_user_directory (severity: high)
  Calendars.Read     → read_calendar       (severity: low)
  
GitHub Examples:
  repo              → read_write_code     (severity: critical)
  admin:org         → org_administration  (severity: critical)
  read:user         → read_user_profile   (severity: low)
  user:email        → read_user_email     (severity: medium)
```

**Normalization algorithm:**

```
def normalize_scope(raw_scope: str, provider_type: ProviderType) -> CanonicalPermission:
    # 1. Exact match lookup in ProviderScope table
    match = db.query(ProviderScope).filter(
        ProviderScope.raw_scope == raw_scope,
        ProviderScope.provider_type == provider_type
    ).first()
    
    if match:
        return CanonicalPermission.from_db(match)
    
    # 2. Pattern match for unknown scopes (e.g., wildcard scopes)
    for pattern in PROVIDER_SCOPE_PATTERNS[provider_type]:
        if pattern.matches(raw_scope):
            return pattern.canonical_permission
    
    # 3. Unknown scope — return with severity=unknown, log for review
    log_unknown_scope(raw_scope, provider_type)
    return CanonicalPermission(
        raw_scope=raw_scope,
        canonical_id="unknown",
        display_name=f"Unknown permission: {raw_scope}",
        severity=PermissionSeverity.MEDIUM,  # Conservative default
        data_classifications=[]
    )
```

---

## Planned Connectors

### Priority 1 (Hackathon Goal): Google Workspace Admin SDK

**Data Available:**
- List of all OAuth applications authorized across the organization
- Scopes granted to each application
- User who authorized each application
- Authorization date
- User list for context

**API Used:** Google Workspace Admin SDK — Directory API + Reports API

**Authentication:** Service Account with domain-wide delegation (most appropriate for organization-level audit)

**Security considerations:**
- Service account key stored encrypted, referenced by ID only
- Minimum required Admin SDK scopes only
- Read-only access; no write operations to provider
- Response validation on all fields before normalization

---

### Priority 2 (Stretch Goal): Microsoft 365

**Data Available:**
- OAuth app registrations and their grants
- Service principal permissions
- App consent records

**API Used:** Microsoft Graph API — `/v1.0/servicePrincipals`, `/v1.0/oauth2PermissionGrants`

**Authentication:** App registration with application permissions (audit-level read-only)

---

### Priority 3 (Future): GitHub

**Data Available:**
- OAuth Apps authorized by organization members
- GitHub App installations
- Fine-grained access tokens

**API Used:** GitHub REST API — `/orgs/{org}/installations`, `/user/installations`

---

### Priority 4 (Future): Slack

**Data Available:**
- Installed apps and their OAuth scopes
- App event subscriptions

**API Used:** Slack Admin API

---

### Priority 5 (Future): Generic OAuth Audit

A generic connector that can read OAuth authorization lists from any provider that supports a standard discovery endpoint.

---

## Sync Architecture

### Sync Lifecycle

```
1. Connector.validate_credentials()
   ↓ (fail fast if credentials invalid)
2. Connector.discover_applications()
   ↓ returns: List[ApplicationDiscoveryResult]
3. NormalizationEngine.normalize(results)
   ↓ returns: List[CanonicalApplicationData]
4. SyncProcessor.upsert_applications(canonical_data, org_id)
   ↓ creates/updates ApplicationInstance records
5. SyncProcessor.detect_changes(previous_state, new_state)
   ↓ detects new apps, removed apps, permission changes
6. PermissionChangeDetector.flag_changes(changes)
   ↓ creates RiskFindings for permission expansions
7. RiskEngine.recalculate_affected_scores(changed_app_ids)
   ↓ updates ApplicationInstance.risk_score
8. AuditLog.record_sync(org_id, sync_result)
```

### Sync Scheduling

```
Default sync frequency: Every 24 hours (configurable)
On-demand sync: Available for Admin users
Post-remediation sync: Triggered 5 minutes after revocation action
```

---

## Manual Entry Mode

For organizations without live connectors, or for applications from providers without connectors:

- UI form to manually register an application
- Fields: name, vendor, category, authorized_by, authorized_at, permissions (multi-select from catalog)
- Business purpose declaration
- Manual entries are clearly labeled as "Manually Entered" with lower confidence level
- Risk scoring still applies; confidence level = Low

---

## Demo Mode / Seeded Data

For the hackathon demonstration, a rich seed dataset must be available:

**Seed data requirements:**
- 15–20 ApplicationInstances representing realistic small-org usage
- Mix of active, dormant, and shadow applications
- Multiple vendors (Google, Microsoft, Slack, GitHub, HubSpot, Zapier, etc.)
- Realistic permission grants including excess permissions
- Data assets with classification
- Pre-computed risk scores with explanations
- At least 2 attack paths
- Timeline of historical permission changes
- Mix of open and resolved findings

**Seed data quality is a competitive advantage.** Judges will scrutinize the demo data.

---

## Integration Security Considerations

| Risk | Control |
|---|---|
| Credential theft | Credentials encrypted at rest; never in logs; referenced by ID |
| SSRF via connector | Provider URLs hardcoded in connector; no user-supplied URLs |
| Malicious API responses | All response fields validated and sanitized |
| Connector failure cascade | Each connector is isolated; failure logged but doesn't break other connectors |
| Prompt injection via app names | App names sanitized before any AI context injection |
| Over-privilege of connector account | Minimum required provider permissions documented per connector |

---

*Integration concept version 1.0 — Architecture defined. Google Workspace connector is Phase 1 priority.*
