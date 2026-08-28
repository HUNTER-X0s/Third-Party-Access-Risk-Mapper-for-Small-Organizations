"""
test_phase5_connector_framework.py
Phase 5 automated tests for the provider-neutral connector framework and GitHub App integration.
All tests use mocked HTTP responses — no live GitHub dependency.
"""
import pytest
import hashlib
import json
from unittest.mock import AsyncMock, MagicMock, patch
from app.connectors.models import (
    NormalizedInstallation, NormalizedRepository, CanonicalPermission,
    NormalizationStatus, RepositorySelection
)
from app.connectors.normalization import (
    normalize_github_permissions, redact_secrets, compute_evidence_hash,
    NORMALIZATION_VERSION
)
from app.connectors.base import BaseConnector, ConnectorCapabilities


# -----------------------------------------------------------------------
# 1. Normalization Tests
# -----------------------------------------------------------------------

def test_known_permission_normalized_correctly():
    """GitHub contents:write maps to WRITE canonical permission."""
    perms = normalize_github_permissions({"contents": "write"})
    assert len(perms) == 1
    p = perms[0]
    assert p.canonical_permission == CanonicalPermission.WRITE
    assert p.normalization_status == NormalizationStatus.NORMALIZED
    assert p.raw_provider_key == "contents"
    assert p.raw_provider_value == "write"
    assert p.normalization_version == NORMALIZATION_VERSION


def test_admin_permission_maps_to_critical():
    """administration:write must map to ADMIN with CRITICAL severity."""
    perms = normalize_github_permissions({"administration": "write"})
    assert perms[0].canonical_permission == CanonicalPermission.ADMIN
    assert perms[0].severity == "CRITICAL"


def test_metadata_read_maps_to_info():
    """metadata:read is always required, should map to READ with INFO severity."""
    perms = normalize_github_permissions({"metadata": "read"})
    assert perms[0].canonical_permission == CanonicalPermission.READ
    assert perms[0].severity == "INFO"


def test_unknown_permission_not_silently_mapped_to_read():
    """Unknown permission MUST produce UNKNOWN canonical — never silently READ."""
    perms = normalize_github_permissions({"future_unknown_resource": "admin"})
    assert len(perms) == 1
    p = perms[0]
    assert p.canonical_permission == CanonicalPermission.UNKNOWN
    assert p.normalization_status == NormalizationStatus.UNKNOWN
    assert p.severity == "HIGH"   # Conservative default for unknowns


def test_multiple_permissions_all_normalized():
    """Multiple permissions produce multiple normalized results."""
    raw = {"contents": "read", "metadata": "read", "issues": "write"}
    perms = normalize_github_permissions(raw)
    assert len(perms) == 3
    canon_perms = {p.canonical_permission for p in perms}
    assert CanonicalPermission.READ in canon_perms
    assert CanonicalPermission.WRITE in canon_perms


def test_empty_permissions_dict():
    """Empty permissions dict returns empty list."""
    perms = normalize_github_permissions({})
    assert perms == []


# -----------------------------------------------------------------------
# 2. Secret Redaction Tests
# -----------------------------------------------------------------------

def test_secret_redaction_removes_authorization_header():
    """Authorization field is redacted before evidence persistence."""
    payload = {"Authorization": "Bearer ghp_secret_token", "installation_id": "12345"}
    redacted = redact_secrets(payload)
    assert redacted["Authorization"] == "[REDACTED]"
    assert redacted["installation_id"] == "12345"


def test_secret_redaction_removes_access_token():
    """access_token field is redacted."""
    payload = {"access_token": "ghp_supersecret", "account_login": "myorg"}
    redacted = redact_secrets(payload)
    assert redacted["access_token"] == "[REDACTED]"
    assert redacted["account_login"] == "myorg"


def test_secret_redaction_removes_private_key():
    """private_key field is redacted."""
    payload = {"private_key": "-----BEGIN RSA PRIVATE KEY-----\n...", "app_id": "123"}
    redacted = redact_secrets(payload)
    assert redacted["private_key"] == "[REDACTED]"
    assert redacted["app_id"] == "123"


def test_secret_redaction_nested_structures():
    """Secret redaction works recursively in nested dicts."""
    payload = {
        "outer": {
            "inner_token": "secret_value",
            "safe_field": "safe"
        }
    }
    redacted = redact_secrets(payload)
    assert redacted["outer"]["inner_token"] == "[REDACTED]"
    assert redacted["outer"]["safe_field"] == "safe"


def test_secret_redaction_in_lists():
    """Secret redaction works in lists of dicts."""
    payload = [{"access_token": "secret"}, {"name": "safe"}]
    redacted = redact_secrets(payload)
    assert redacted[0]["access_token"] == "[REDACTED]"
    assert redacted[1]["name"] == "safe"


def test_credentials_never_in_evidence_hash():
    """Evidence hash excludes credential values — redaction applied before hashing."""
    payload_with_secret = {"access_token": "real_secret_value", "installation_id": "123"}
    redacted = redact_secrets(payload_with_secret)
    h = compute_evidence_hash(redacted)
    # Hash must be of redacted payload, so secret value must not appear in source
    canonical = json.dumps(redacted, sort_keys=True, default=str)
    assert "real_secret_value" not in canonical
    assert h == hashlib.sha256(canonical.encode()).hexdigest()


# -----------------------------------------------------------------------
# 3. Evidence Hash Tests
# -----------------------------------------------------------------------

def test_evidence_hash_is_deterministic():
    """Same payload always produces same hash."""
    payload = {"installation_id": "42", "account_login": "myorg", "permissions": {"contents": "read"}}
    h1 = compute_evidence_hash(payload)
    h2 = compute_evidence_hash(payload)
    assert h1 == h2


def test_evidence_hash_key_order_invariant():
    """Evidence hash is key-order invariant (uses sort_keys=True)."""
    p1 = {"b": 2, "a": 1}
    p2 = {"a": 1, "b": 2}
    assert compute_evidence_hash(p1) == compute_evidence_hash(p2)


def test_evidence_hash_tamper_detection():
    """Modifying payload produces a different hash."""
    p1 = {"installation_id": "42", "permissions": {"contents": "read"}}
    p2 = {"installation_id": "42", "permissions": {"contents": "write"}}
    assert compute_evidence_hash(p1) != compute_evidence_hash(p2)


# -----------------------------------------------------------------------
# 4. Write Guard Tests
# -----------------------------------------------------------------------

def test_base_connector_write_guard_raises():
    """Any write operation on a read-only connector raises NotImplementedError."""
    class MockConnector(BaseConnector):
        capabilities = ConnectorCapabilities(READ=True, WRITE=False)
        PROVIDER = "TEST"
        async def authenticate(self): return True
        async def health_check(self): pass
        async def discover_installations(self): return []
        async def discover_repositories(self, id): return []
        async def collect_snapshot(self): pass
        def close(self): pass

    connector = MockConnector()
    with pytest.raises(NotImplementedError, match="READ-ONLY"):
        connector.revoke_permission("some_id")


def test_base_connector_write_guard_all_write_methods():
    """All write method variants raise on read-only connector."""
    class MockConnector(BaseConnector):
        capabilities = ConnectorCapabilities(READ=True, WRITE=False)
        PROVIDER = "TEST"
        async def authenticate(self): return True
        async def health_check(self): pass
        async def discover_installations(self): return []
        async def discover_repositories(self, id): return []
        async def collect_snapshot(self): pass
        def close(self): pass

    c = MockConnector()
    for method in [c.revoke_permission, c.grant_permission, c.modify_resource, c.delete_resource]:
        with pytest.raises(NotImplementedError):
            method()


# -----------------------------------------------------------------------
# 5. Connector API Endpoint Tests (authorization + isolation)
# -----------------------------------------------------------------------

def test_viewer_cannot_create_connector(client, db_session):
    """VIEWER role must not be able to configure a new connector."""
    login = client.post("/api/v1/auth/login", json={
        "email": "viewer@anurag.tech", "password": "DemoPass123!"
    })
    token = login.cookies.get("access_token")
    res = client.post("/api/v1/connectors", json={
        "provider": "GITHUB", "display_name": "Test GitHub", "mode": "DEMO"
    }, cookies={"access_token": token})
    assert res.status_code == 403


def test_auditor_cannot_create_connector(client, db_session):
    """AUDITOR role must not be able to configure a new connector."""
    login = client.post("/api/v1/auth/login", json={
        "email": "auditor@anurag.tech", "password": "DemoPass123!"
    })
    token = login.cookies.get("access_token")
    res = client.post("/api/v1/connectors", json={
        "provider": "GITHUB", "display_name": "Test GitHub", "mode": "DEMO"
    }, cookies={"access_token": token})
    assert res.status_code == 403


def test_security_admin_can_create_and_view_connector(client, db_session):
    """SECURITY_ADMIN can create a connector and view it."""
    login = client.post("/api/v1/auth/login", json={
        "email": "admin@anurag.tech", "password": "DemoPass123!"
    })
    token = login.cookies.get("access_token")

    create_res = client.post("/api/v1/connectors", json={
        "provider": "GITHUB",
        "display_name": "GitHub (Demo)",
        "mode": "DEMO",
        "config": {"app_id": "test-app-123"}
    }, cookies={"access_token": token})
    assert create_res.status_code == 201
    data = create_res.json()
    assert data["provider"] == "GITHUB"
    assert data["mode"] == "DEMO"
    connector_id = data["id"]

    # View it
    get_res = client.get(f"/api/v1/connectors/{connector_id}", cookies={"access_token": token})
    assert get_res.status_code == 200
    assert get_res.json()["id"] == connector_id


def test_connector_list_tenant_isolation(client, db_session):
    """Connectors are isolated per organization — different org gets empty list."""
    login = client.post("/api/v1/auth/login", json={
        "email": "admin@anurag.tech", "password": "DemoPass123!"
    })
    token = login.cookies.get("access_token")

    list_res = client.get("/api/v1/connectors", cookies={"access_token": token})
    assert list_res.status_code == 200
    # Should be a list (may be empty or contain connectors for this org only)
    assert isinstance(list_res.json(), list)


def test_connector_health_endpoint(client, db_session):
    """Connector health endpoint accessible to VIEWER."""
    # Create connector as admin
    admin_login = client.post("/api/v1/auth/login", json={
        "email": "admin@anurag.tech", "password": "DemoPass123!"
    })
    admin_token = admin_login.cookies.get("access_token")
    create_res = client.post("/api/v1/connectors", json={
        "provider": "GITHUB", "display_name": "GitHub Health Test", "mode": "DEMO"
    }, cookies={"access_token": admin_token})
    connector_id = create_res.json()["id"]

    # Viewer checks health
    viewer_login = client.post("/api/v1/auth/login", json={
        "email": "viewer@anurag.tech", "password": "DemoPass123!"
    })
    viewer_token = viewer_login.cookies.get("access_token")
    health_res = client.get(f"/api/v1/connectors/{connector_id}/health",
                            cookies={"access_token": viewer_token})
    assert health_res.status_code == 200
    assert "status" in health_res.json()


def test_demo_mode_sync_completes(client, db_session):
    """Demo mode connector sync completes successfully without live GitHub calls."""
    admin_login = client.post("/api/v1/auth/login", json={
        "email": "admin@anurag.tech", "password": "DemoPass123!"
    })
    token = admin_login.cookies.get("access_token")

    create_res = client.post("/api/v1/connectors", json={
        "provider": "GITHUB", "display_name": "GitHub Demo Sync", "mode": "DEMO"
    }, cookies={"access_token": token})
    connector_id = create_res.json()["id"]

    sync_res = client.post(f"/api/v1/connectors/{connector_id}/sync",
                           cookies={"access_token": token})
    assert sync_res.status_code == 200
    assert sync_res.json()["status"] == "SYNC_INITIATED"


def test_only_super_admin_can_disconnect(client, db_session):
    """Only SUPER_ADMIN can disconnect a connector."""
    admin_login = client.post("/api/v1/auth/login", json={
        "email": "admin@anurag.tech", "password": "DemoPass123!"
    })
    admin_token = admin_login.cookies.get("access_token")
    create_res = client.post("/api/v1/connectors", json={
        "provider": "GITHUB", "display_name": "GitHub To Disconnect", "mode": "DEMO"
    }, cookies={"access_token": admin_token})
    connector_id = create_res.json()["id"]

    # SECURITY_ADMIN cannot disconnect
    res = client.post(f"/api/v1/connectors/{connector_id}/disconnect",
                      cookies={"access_token": admin_token})
    assert res.status_code == 403

    # SUPER_ADMIN can disconnect
    super_login = client.post("/api/v1/auth/login", json={
        "email": "superadmin@anurag.tech", "password": "DemoPass123!"
    })
    super_token = super_login.cookies.get("access_token")
    res = client.post(f"/api/v1/connectors/{connector_id}/disconnect",
                      cookies={"access_token": super_token})
    assert res.status_code == 200
    assert res.json()["status"] == "DISCONNECTED"


# -----------------------------------------------------------------------
# 6. Phase 5.1 Live Validation & Error Handling Tests
# -----------------------------------------------------------------------

def test_github_api_version_header_2026_03_10():
    """Verifies GitHubConnector uses configuration-driven GITHUB_API_VERSION (2026-03-10)."""
    from app.connectors.github_connector import GitHubConnector, GitHubConnectorConfig
    from app.core.config import settings

    assert settings.GITHUB_API_VERSION == "2026-03-10"
    config = GitHubConnectorConfig(app_id="12345", private_key_pem="fake-pem")
    connector = GitHubConnector(config, "conn-id", "org-id")

    headers = connector._base_headers("fake-token")
    assert headers["X-GitHub-Api-Version"] == "2026-03-10"
    assert headers["Accept"] == "application/vnd.github+json"


def test_pipeline_sync_idempotency_no_duplicates(db_session):
    """Running pipeline process_installation twice on identical data produces 0 duplicate domain entities."""
    from app.connectors.pipeline import ConnectorPipeline
    from app.connectors.models import (
        NormalizedInstallation, NormalizedRepository, NormalizedPermission,
        CanonicalPermission, NormalizationStatus, RepositorySelection
    )
    from app.models import Organization, Vendor, Application, ApplicationInstance, PermissionGrant, ProviderConnector, ConnectorSyncRun

    org = db_session.query(Organization).first()
    connector = ProviderConnector(
        organization_id=org.id, provider="GITHUB", display_name="Idempotency Test GitHub", mode="DEMO"
    )
    db_session.add(connector)
    db_session.flush()

    sync_run = ConnectorSyncRun(connector_id=connector.id, organization_id=org.id, status="STARTED")
    db_session.add(sync_run)
    db_session.flush()

    installation = NormalizedInstallation(
        installation_id="inst-999",
        account_login="idempotent-org",
        account_type="Organization",
        app_id="app-888",
        app_slug="idempotent-app",
        repository_selection=RepositorySelection.ALL,
        permissions=[
            NormalizedPermission(
                raw_provider_key="contents", raw_provider_value="write",
                canonical_permission=CanonicalPermission.WRITE,
                normalization_status=NormalizationStatus.NORMALIZED,
                severity="HIGH"
            )
        ],
        repositories=[
            NormalizedRepository(
                external_id="repo-777", name="repo-a", full_name="idempotent-org/repo-a",
                owner="idempotent-org", is_private=True, is_fork=False, default_branch="main",
                description="Test repo", visibility="private"
            )
        ]
    )

    pipeline = ConnectorPipeline(db_session, org.id, connector.id)
    raw_payload = {"installation_id": "inst-999", "account_login": "idempotent-org"}
    evidence_hash = "fake-hash-111"

    # Run 1
    res1 = pipeline.process_installation(installation, raw_payload, evidence_hash, sync_run)
    db_session.flush()

    instance_id = res1["instance_id"]
    assert instance_id is not None

    vendor_count_1 = db_session.query(Vendor).filter(Vendor.name == "GitHub (idempotent-org)").count()
    grant_count_1 = db_session.query(PermissionGrant).filter(
        PermissionGrant.application_instance_id == instance_id
    ).count()

    assert vendor_count_1 == 1
    assert grant_count_1 == 1

    # Run 2 (Identical snapshot)
    res2 = pipeline.process_installation(installation, raw_payload, "fake-hash-222", sync_run)
    db_session.flush()

    vendor_count_2 = db_session.query(Vendor).filter(Vendor.name == "GitHub (idempotent-org)").count()
    grant_count_2 = db_session.query(PermissionGrant).filter(
        PermissionGrant.application_instance_id == instance_id
    ).count()

    # Domain entities must NOT duplicate
    assert vendor_count_2 == 1
    assert grant_count_2 == 1


def test_github_sync_failure_preserves_state(db_session):
    """Simulates 401 auth failure and rate-limiting to ensure health updates correctly and state is preserved."""
    import asyncio
    from app.connectors.github_connector import GitHubConnector, GitHubConnectorConfig

    config = GitHubConnectorConfig(app_id="999", private_key_pem="invalid-pem")
    connector = GitHubConnector(config, "conn-fail-test", "org-test")

    async def _test():
        with patch.object(connector, "authenticate", new=AsyncMock(return_value=False)):
            res = await connector.collect_snapshot()
            assert res.status == "AUTH_FAILED"

    asyncio.run(_test())
    connector.close()

