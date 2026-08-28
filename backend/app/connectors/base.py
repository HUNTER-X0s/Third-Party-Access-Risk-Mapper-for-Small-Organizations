"""
connectors/base.py
Provider-neutral abstract connector interface.
All provider connectors MUST inherit from BaseConnector.
WRITE operations are architecturally prohibited in Phase 5.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from app.connectors.models import (
    NormalizedInstallation, ConnectorHealth, SyncResult
)


@dataclass
class ConnectorCapabilities:
    """Declares what a connector can do. Phase 5: READ=True, WRITE=False always."""
    READ: bool = True
    WRITE: bool = False   # Phase 5: All connectors are strictly read-only


class BaseConnector(ABC):
    """
    Provider-neutral connector interface.
    Every provider connector (GitHub, Google Workspace, MS365, ...) MUST implement this.
    The write guard ensures no connector accidentally performs mutations.
    """

    # Must be declared by each subclass
    capabilities: ConnectorCapabilities = ConnectorCapabilities(READ=True, WRITE=False)
    PROVIDER: str = "UNKNOWN"
    API_VERSION: str = "UNVERSIONED"

    def _write_guard(self) -> None:
        """Architectural guard: raises NotImplementedError if WRITE=False (Phase 5 invariant)."""
        if not self.capabilities.WRITE:
            raise NotImplementedError(
                f"Connector '{self.PROVIDER}' is READ-ONLY. "
                "WRITE operations are prohibited in Phase 5. "
                "To enable write operations, set capabilities.WRITE=True after explicit review."
            )

    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Authenticate with the provider. Returns True on success.
        Must not log or persist credentials.
        """
        ...

    @abstractmethod
    async def health_check(self) -> ConnectorHealth:
        """Check current connectivity and credential validity."""
        ...

    @abstractmethod
    async def discover_installations(self) -> List[NormalizedInstallation]:
        """Discover all provider installations accessible to this connector."""
        ...

    @abstractmethod
    async def discover_repositories(self, installation_id: str) -> List:
        """Discover repositories/resources accessible within a given installation."""
        ...

    @abstractmethod
    async def collect_snapshot(self) -> SyncResult:
        """
        Run a full collection cycle.
        Produces raw evidence, normalized output, and a SyncResult.
        """
        ...

    @abstractmethod
    def close(self) -> None:
        """Clean up resources (HTTP clients, etc.)."""
        ...

    # --- Write operations (all prohibited in Phase 5) ---

    def revoke_permission(self, *args, **kwargs):
        self._write_guard()

    def grant_permission(self, *args, **kwargs):
        self._write_guard()

    def modify_resource(self, *args, **kwargs):
        self._write_guard()

    def delete_resource(self, *args, **kwargs):
        self._write_guard()
