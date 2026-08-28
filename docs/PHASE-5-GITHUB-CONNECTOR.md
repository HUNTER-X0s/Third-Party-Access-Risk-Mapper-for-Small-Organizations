# AccessGuard Phase 5 — Read-Only GitHub App Connector Specification

## Overview

The GitHub App connector allows AccessGuard to discover GitHub App installations, permission grants, and accessible repositories across an organization.

---

## Authentication Flow

GitHub Apps use a two-step authentication model:

1. **App-Level Authentication (App JWT)**:
   - AccessGuard generates a RS256 JSON Web Token signed with the App's PEM private key (`settings.GITHUB_PRIVATE_KEY`).
   - Claims: `iat` (now − 60s clock skew), `exp` (now + 10m), `iss` = `settings.GITHUB_APP_ID`.
   - Used for administrative endpoints: `GET /app`, `GET /app/installations`, `GET /rate_limit`.
   - **Security**: The App JWT is generated in-memory per call and is NEVER logged, stored, or sent to clients.

2. **Installation-Level Authentication (Installation Access Token)**:
   - AccessGuard exchanges the App JWT for an Installation Access Token via `POST /app/installations/{installation_id}/access_tokens`.
   - Used for resource endpoints: `GET /installation/repositories`.
   - **Security**: The Installation Access Token is short-lived (1 hour) and is immediately discarded from memory after repository collection. It is NEVER persisted in SQLite/PostgreSQL database tables.

---

## Endpoints Consumed (Read-Only)

All requests include:
- `Accept: application/vnd.github+json`
- `X-GitHub-Api-Version: 2022-11-28`
- Explicit HTTP timeout: `connect=10.0s, read=20.0s`

| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| `/app` | `GET` | App JWT | Authenticate connector credentials |
| `/rate_limit` | `GET` | App JWT | Check API rate limit reset times |
| `/app/installations` | `GET` | App JWT | Discover all installations (paginated) |
| `/app/installations/{id}/access_tokens` | `POST` | App JWT | Obtain ephemeral installation token |
| `/installation/repositories` | `GET` | Installation Token | List accessible repositories (paginated) |

---

## Rate Limit & Timeout Handling

- **Primary Limit**: 5,000 requests/hour per installation.
- **Header Parsing**: `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After`.
- **Rate-Limited Behavior**: When status code `429` or `403` with `X-RateLimit-Remaining: 0` occurs:
  1. Connector status transitions to `RATE_LIMITED`.
  2. `rate_limit_reset_at` timestamp is extracted.
  3. Collection halts gracefully without crashing.
  4. The last trusted `SecuritySnapshot` is preserved.
  5. AccessGuard does NOT loop or hammer the GitHub API.

---

## Pagination Strategy

- Requests use `per_page=100` (GitHub maximum).
- Responses parse the standard GitHub `Link` header looking for `rel="next"`.
- Supports single-page, multi-page, empty page, and last-page conditions.
