# Official GitHub API References & Versioning Record

**Date Recorded:** 2026-08-14  
**Pinned API Version:** `2026-03-10` (Updated in Phase 5.1 from `2022-11-28`)  
**Media Type:** `application/vnd.github+json`  
**Configuration Source:** `settings.GITHUB_API_VERSION` (`config.py`)

---

## Authoritative Documentation References

The implementation of the GitHub App Connector in AccessGuard Phase 5 & 5.1 is built directly against the official GitHub REST API documentation:

1. **GitHub App Authentication**:
   - URL: `https://docs.github.com/en/rest/apps/apps#about-github-apps`
   - URL: `https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app`
   - Key details: App JWT signed via RS256, max 10 min TTL, `iss` claim = App ID.

2. **GitHub App Installations & Access Tokens**:
   - URL: `https://docs.github.com/en/rest/apps/installations?apiVersion=2026-03-10`
   - URL: `https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation`
   - Endpoints: `GET /app/installations`, `POST /app/installations/{installation_id}/access_tokens`.

3. **Repository Discovery & Selection**:
   - URL: `https://docs.github.com/en/rest/apps/installations#list-repositories-accessible-to-the-app-installation`
   - Endpoint: `GET /installation/repositories`
   - Query Parameters: `per_page` (default 30, max 100), `page`.
   - Response Fields: `total_count`, `repository_selection` (`all` or `selected`), `repositories` (array).

4. **GitHub App Permission Semantics**:
   - URL: `https://docs.github.com/en/rest/overview/permissions-required-for-github-apps`
   - Permission format: Dict of resource key -> access level (`read`, `write`, `admin`).

5. **Rate Limits & Headers**:
   - URL: `https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api`
   - Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After`.

---

## Exact Header Requirements

Every HTTP request sent by AccessGuard's `GitHubConnector` includes:
```http
Authorization: Bearer <TOKEN>
Accept: application/vnd.github+json
X-GitHub-Api-Version: 2026-03-10
User-Agent: AccessGuard-RiskMapper/1.5.0
```
