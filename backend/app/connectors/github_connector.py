"""
connectors/github_connector.py
Read-only GitHub App connector for AccessGuard Phase 5.

Authentication: 2-step GitHub App flow
  Step 1: App JWT (RS256, signed with PEM private key, 10-minute TTL)
  Step 2: Installation Access Token (POST /app/installations/{id}/access_tokens)

API Version: 2022-11-28 (pinned, never relies on provider defaults)
All HTTP calls: explicit 30-second timeout (10s connect, 20s read)
Rate limits: honored via X-RateLimit-* headers; connector marked RATE_LIMITED, no hammering
Pagination: fully handled via Link header / per_page=100
Write guard: inherited from BaseConnector — all mutation methods raise NotImplementedError
"""
import time
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

import jwt
import httpx

from app.connectors.base import BaseConnector, ConnectorCapabilities
from app.connectors.models import (
    NormalizedInstallation, NormalizedRepository, ConnectorHealth,
    SyncResult, RepositorySelection
)
from app.connectors.normalization import (
    normalize_github_permissions, redact_secrets, compute_evidence_hash
)

logger = logging.getLogger(__name__)

from app.core.config import settings

# GitHub API constants
GITHUB_ACCEPT = "application/vnd.github+json"
DEFAULT_TIMEOUT = httpx.Timeout(connect=10.0, read=20.0, write=None, pool=None)
PAGE_SIZE = 100  # Max per_page for GitHub API


@dataclass
class GitHubConnectorConfig:
    """Non-secret configuration for the GitHub connector. Credentials from environment only."""
    app_id: str
    private_key_pem: str    # PEM string — never logged, never persisted
    base_url: str = "https://api.github.com"
    api_version: str = settings.GITHUB_API_VERSION
    timeout_seconds: int = 30


class GitHubConnector(BaseConnector):
    """
    Read-only GitHub App connector.
    Capabilities: READ=True, WRITE=False (enforced by BaseConnector write guard)
    """
    PROVIDER = "GITHUB"
    API_VERSION = settings.GITHUB_API_VERSION
    capabilities = ConnectorCapabilities(READ=True, WRITE=False)

    def __init__(self, config: GitHubConnectorConfig, connector_id: str, org_id: str):
        self.config = config
        self.connector_id = connector_id
        self.org_id = org_id
        self._client: Optional[httpx.AsyncClient] = None
        self._rate_limit_reset: Optional[datetime] = None
        self._last_error: Optional[str] = None

    # ------------------------------------------------------------------
    # Internal HTTP helpers
    # ------------------------------------------------------------------

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)
        return self._client

    def _make_app_jwt(self) -> str:
        """
        Generate a GitHub App JWT using RS256 + PEM private key.
        10-minute expiry. Backdated 60s to account for clock skew.
        The JWT is NEVER logged or persisted.
        """
        now = int(time.time())
        payload = {
            "iat": now - 60,
            "exp": now + (10 * 60),
            "iss": str(self.config.app_id),
        }
        return jwt.encode(payload, self.config.private_key_pem, algorithm="RS256")

    def _base_headers(self, token: str, token_type: str = "Bearer") -> Dict[str, str]:
        return {
            "Authorization": f"{token_type} {token}",
            "Accept": GITHUB_ACCEPT,
            "X-GitHub-Api-Version": self.config.api_version,
        }

    def _check_rate_limit(self, response: httpx.Response) -> bool:
        """
        Returns True if rate-limited. Records reset time from headers.
        Does NOT retry — caller records RATE_LIMITED state.
        """
        if response.status_code == 429 or (
            response.status_code == 403 and "X-RateLimit-Remaining" in response.headers
            and response.headers.get("X-RateLimit-Remaining") == "0"
        ):
            reset_ts = response.headers.get("X-RateLimit-Reset")
            retry_after = response.headers.get("Retry-After")
            if reset_ts:
                self._rate_limit_reset = datetime.fromtimestamp(int(reset_ts), tz=timezone.utc)
            elif retry_after:
                self._rate_limit_reset = datetime.fromtimestamp(
                    int(time.time()) + int(retry_after), tz=timezone.utc
                )
            return True
        return False

    async def _paginate(self, url: str, headers: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Fully paginate a GitHub API endpoint using per_page=100 + Link header.
        Handles: single-page, multi-page, empty, last-page.
        Stops on rate limit or error — does NOT loop indefinitely.
        """
        client = self._get_client()
        results = []
        current_url = url
        params = {"per_page": PAGE_SIZE, "page": 1}

        while current_url:
            try:
                response = await client.get(current_url, headers=headers, params=params)
            except httpx.TimeoutException as e:
                self._last_error = f"Timeout fetching {current_url}: {e}"
                logger.warning(self._last_error)
                break
            except httpx.HTTPError as e:
                self._last_error = f"HTTP error fetching {current_url}: {e}"
                logger.warning(self._last_error)
                break

            if self._check_rate_limit(response):
                self._last_error = f"Rate limited by GitHub API. Reset at: {self._rate_limit_reset}"
                logger.warning(self._last_error)
                break

            if response.status_code != 200:
                self._last_error = f"GitHub API error {response.status_code}: {response.text[:200]}"
                logger.warning(self._last_error)
                break

            try:
                page_data = response.json()
            except Exception:
                self._last_error = "Malformed JSON response from GitHub API"
                logger.warning(self._last_error)
                break

            if isinstance(page_data, dict) and "repositories" in page_data:
                # /installation/repositories wraps repos in a dict
                results.extend(page_data.get("repositories", []))
            elif isinstance(page_data, list):
                results.extend(page_data)
            else:
                results.append(page_data)

            # Parse Link header for next page
            link_header = response.headers.get("Link", "")
            next_url = self._parse_next_link(link_header)
            current_url = next_url
            params = {}  # Next URL already contains query params

        return results

    @staticmethod
    def _parse_next_link(link_header: str) -> Optional[str]:
        """Parse GitHub's Link header to find the 'next' page URL."""
        if not link_header:
            return None
        for part in link_header.split(","):
            segments = part.strip().split(";")
            if len(segments) == 2 and 'rel="next"' in segments[1].strip():
                return segments[0].strip().strip("<>")
        return None

    # ------------------------------------------------------------------
    # Public connector interface
    # ------------------------------------------------------------------

    async def authenticate(self) -> bool:
        """Authenticate as GitHub App using RS256 JWT. Tests /app endpoint."""
        try:
            app_jwt = self._make_app_jwt()
            client = self._get_client()
            response = await client.get(
                f"{self.config.base_url}/app",
                headers=self._base_headers(app_jwt)
            )
            if response.status_code == 200:
                logger.info("GitHub App authentication successful (app_id=%s)", self.config.app_id)
                return True
            self._last_error = f"GitHub App auth failed: HTTP {response.status_code}"
            logger.warning(self._last_error)
            return False
        except Exception as e:
            self._last_error = f"Authentication exception: {e}"
            logger.error(self._last_error)
            return False

    async def health_check(self) -> ConnectorHealth:
        """Check rate limit status and auth validity."""
        try:
            app_jwt = self._make_app_jwt()
            client = self._get_client()
            response = await client.get(
                f"{self.config.base_url}/rate_limit",
                headers=self._base_headers(app_jwt)
            )
            if response.status_code == 200:
                return ConnectorHealth(
                    status="HEALTHY",
                    last_sync_at=None, last_attempted_at=datetime.now(timezone.utc),
                    last_error=None, apps_discovered=0, permissions_discovered=0,
                    data_freshness_seconds=None
                )
            if self._check_rate_limit(response):
                return ConnectorHealth(
                    status="RATE_LIMITED",
                    last_sync_at=None, last_attempted_at=datetime.now(timezone.utc),
                    last_error=self._last_error, apps_discovered=0, permissions_discovered=0,
                    data_freshness_seconds=None, rate_limit_reset_at=self._rate_limit_reset
                )
        except Exception as e:
            self._last_error = str(e)

        return ConnectorHealth(
            status="UNAVAILABLE",
            last_sync_at=None, last_attempted_at=datetime.now(timezone.utc),
            last_error=self._last_error, apps_discovered=0, permissions_discovered=0,
            data_freshness_seconds=None
        )

    async def discover_installations(self) -> List[NormalizedInstallation]:
        """
        Discover all GitHub App installations.
        Endpoint: GET /app/installations (App JWT auth, paginated)
        """
        app_jwt = self._make_app_jwt()
        headers = self._base_headers(app_jwt)
        raw_installations = await self._paginate(
            f"{self.config.base_url}/app/installations", headers
        )
        return [self._normalize_installation(inst) for inst in raw_installations
                if isinstance(inst, dict) and "id" in inst]

    def _normalize_installation(self, raw: Dict[str, Any]) -> NormalizedInstallation:
        """Convert a raw GitHub installation object into a NormalizedInstallation."""
        raw_permissions = raw.get("permissions", {})
        normalized_permissions = normalize_github_permissions(raw_permissions)

        # Validate external data — treat all provider fields as untrusted
        installation_id = str(raw.get("id", "unknown"))
        account = raw.get("account", {}) or {}
        account_login = str(account.get("login", "unknown"))
        account_type = str(account.get("type", "Unknown"))
        app_id = str(raw.get("app_id", self.config.app_id))
        app_slug = str(raw.get("app_slug", "unknown"))

        repo_sel_raw = raw.get("repository_selection", "unknown")
        try:
            repo_selection = RepositorySelection(repo_sel_raw)
        except ValueError:
            repo_selection = RepositorySelection.NONE

        return NormalizedInstallation(
            installation_id=installation_id,
            account_login=account_login,
            account_type=account_type,
            app_id=app_id,
            app_slug=app_slug,
            repository_selection=repo_selection,
            permissions=normalized_permissions,
            is_suspended=raw.get("suspended_at") is not None,
            suspension_reason=raw.get("suspended_by", {}).get("login") if raw.get("suspended_at") else None,
            created_at=raw.get("created_at"),
            updated_at=raw.get("updated_at"),
        )

    async def discover_repositories(self, installation_id: str) -> List[NormalizedRepository]:
        """
        Get an installation access token then discover repositories.
        Endpoint: POST /app/installations/{id}/access_tokens → GET /installation/repositories
        """
        app_jwt = self._make_app_jwt()
        client = self._get_client()

        # Step 1: Get installation access token (short-lived, never persisted)
        token_response = await client.post(
            f"{self.config.base_url}/app/installations/{installation_id}/access_tokens",
            headers=self._base_headers(app_jwt)
        )
        if token_response.status_code != 201:
            self._last_error = f"Failed to get installation token: HTTP {token_response.status_code}"
            logger.warning(self._last_error)
            return []

        token_data = token_response.json()
        installation_token = token_data.get("token")
        if not installation_token:
            self._last_error = "Installation token missing from response"
            return []

        # Step 2: List repos accessible to this installation (token NEVER stored in DB)
        repo_headers = self._base_headers(installation_token)
        raw_repos = await self._paginate(
            f"{self.config.base_url}/installation/repositories", repo_headers
        )

        # Explicitly discard the token — it is ephemeral
        del installation_token

        return [self._normalize_repository(r) for r in raw_repos if isinstance(r, dict)]

    def _normalize_repository(self, raw: Dict[str, Any]) -> NormalizedRepository:
        """Convert raw GitHub repository object to NormalizedRepository."""
        owner = raw.get("owner", {}) or {}
        return NormalizedRepository(
            external_id=str(raw.get("id", "unknown")),
            name=str(raw.get("name", "unknown")),
            full_name=str(raw.get("full_name", "unknown")),
            owner=str(owner.get("login", "unknown")),
            is_private=bool(raw.get("private", False)),
            is_fork=bool(raw.get("fork", False)),
            default_branch=str(raw.get("default_branch", "main")),
            description=raw.get("description"),
            visibility=str(raw.get("visibility", "private")),
            classification="UNCLASSIFIED",  # Classification must be user-assigned
            raw_metadata={
                "github_id": raw.get("id"),
                "topics": raw.get("topics", []),
                "size": raw.get("size"),
                "pushed_at": raw.get("pushed_at"),
                "updated_at": raw.get("updated_at"),
            }
        )

    def build_raw_evidence_payload(self, installation: NormalizedInstallation,
                                    repositories: List[NormalizedRepository]) -> Tuple[Dict, str]:
        """
        Build the raw evidence payload for persistence.
        Applies secret redaction before returning.
        Returns (redacted_payload, sha256_hash).
        """
        payload = {
            "provider": "GITHUB",
            "api_version": self.API_VERSION,
            "connector_id": self.connector_id,
            "organization_id": self.org_id,
            "installation_id": installation.installation_id,
            "account_login": installation.account_login,
            "account_type": installation.account_type,
            "app_id": installation.app_id,
            "app_slug": installation.app_slug,
            "repository_selection": installation.repository_selection.value,
            "raw_permissions": {
                p.raw_provider_key: p.raw_provider_value
                for p in installation.permissions
            },
            "repositories": [
                {
                    "id": r.external_id,
                    "full_name": r.full_name,
                    "is_private": r.is_private,
                    "visibility": r.visibility,
                }
                for r in repositories
            ],
            "is_suspended": installation.is_suspended,
        }
        redacted = redact_secrets(payload)
        evidence_hash = compute_evidence_hash(redacted)
        return redacted, evidence_hash

    async def collect_snapshot(self) -> SyncResult:
        """
        Full collection cycle. Returns SyncResult.
        On failure: returns FAILED SyncResult without corrupting existing state.
        """
        start = time.time()
        try:
            auth_ok = await self.authenticate()
            if not auth_ok:
                return SyncResult(
                    connector_id=self.connector_id, status="AUTH_FAILED",
                    records_collected=0, records_normalized=0, findings_created=0,
                    snapshot_id=None, error_message=self._last_error,
                    duration_seconds=int(time.time() - start)
                )
            installations = await self.discover_installations()
            all_repos = []
            for inst in installations:
                repos = await self.discover_repositories(inst.installation_id)
                inst.repositories = repos
                all_repos.extend(repos)

            return SyncResult(
                connector_id=self.connector_id, status="COMPLETED",
                records_collected=len(installations),
                records_normalized=len(installations),
                findings_created=0,
                snapshot_id=None,
                error_message=None,
                duration_seconds=int(time.time() - start),
                installations=installations,
            )
        except Exception as e:
            self._last_error = str(e)
            logger.error("GitHub connector collect_snapshot failed: %s", e)
            return SyncResult(
                connector_id=self.connector_id, status="FAILED",
                records_collected=0, records_normalized=0, findings_created=0,
                snapshot_id=None, error_message=str(e),
                duration_seconds=int(time.time() - start),
            )

    def close(self) -> None:
        if self._client and not self._client.is_closed:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._client.aclose())
                else:
                    loop.run_until_complete(self._client.aclose())
            except Exception:
                pass
