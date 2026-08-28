# AccessGuard Phase 5 — Normalization Mapping Specification

**Normalization Version:** `1.0.0`

---

## Canonical Permission Mapping Table

Provider scope strings imported from GitHub API responses are mapped into AccessGuard canonical permissions according to the following mapping table:

| GitHub Resource | GitHub Access Level | Canonical Permission | Risk Severity | Security Notes |
|---|---|---|---|---|
| `contents` | `read` | `READ` | LOW | Read repository contents |
| `contents` | `write` | `WRITE` | HIGH | Modify code & commit history |
| `metadata` | `read` | `READ` | INFO | Required metadata read (always granted) |
| `administration` | `read` | `READ` | MEDIUM | Read org/repo settings |
| `administration` | `write` | `ADMIN` | CRITICAL | Full administrative control |
| `members` | `read` | `READ` | MEDIUM | Read org membership |
| `members` | `write` | `WRITE` | HIGH | Add/remove org members |
| `issues` | `read` | `READ` | LOW | Read issue tracker |
| `issues` | `write` | `WRITE` | MEDIUM | Create & edit issues |
| `pull_requests` | `read` | `READ` | LOW | Read pull requests |
| `pull_requests` | `write` | `WRITE` | MEDIUM | Create & merge pull requests |
| `actions` | `read` | `READ` | MEDIUM | Read CI/CD workflows |
| `actions` | `write` | `EXECUTE` | HIGH | Trigger & manage CI/CD pipelines |
| `secrets` | `read` | `READ` | CRITICAL | Read org & repository secrets |
| `secrets` | `write` | `WRITE` | CRITICAL | Create/update secrets |
| `security_events` | `read` | `READ` | MEDIUM | Read code scanning alerts |
| `security_events` | `write` | `WRITE` | HIGH | Dismiss security alerts |
| `repository_hooks` | `write` | `CONFIGURE` | HIGH | Manage repository webhooks |
| `organization_hooks` | `write` | `ADMIN` | CRITICAL | Manage organization-wide webhooks |

---

## Conservative Unknown Permission Policy

If GitHub introduces a new permission scope key not present in `GITHUB_PERMISSION_MAP`:

1. AccessGuard does **NOT** drop the scope.
2. AccessGuard does **NOT** silently assign `READ` or `LOW` risk.
3. AccessGuard assigns `CanonicalPermission.UNKNOWN`, `NormalizationStatus.UNKNOWN`, and `HIGH` severity.
4. An integration warning is recorded: `"Unknown GitHub permission '{resource}:{level}' — requires manual mapping review."`
5. The application remains visible in inventory with an alert flag for human security admin review.
