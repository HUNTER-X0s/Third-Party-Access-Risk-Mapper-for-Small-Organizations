"""
connectors/models.py
Pure-Python dataclasses for normalized connector output.
These are the canonical objects that cross the connector boundary into the domain layer.
No provider-specific objects may pass through this boundary.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class CanonicalPermission(str, Enum):
    """AccessGuard canonical permission set. Provider-specific permissions map to these."""
    READ = "READ"
    WRITE = "WRITE"
    DELETE = "DELETE"
    EXPORT = "EXPORT"
    SHARE = "SHARE"
    ADMIN = "ADMIN"
    CONFIGURE = "CONFIGURE"
    EXECUTE = "EXECUTE"
    UNKNOWN = "UNKNOWN"   # Unknown permission — surfaces for review, NOT silently mapped to READ


class NormalizationStatus(str, Enum):
    NORMALIZED = "NORMALIZED"
    UNKNOWN = "UNKNOWN"       # Permission not in mapping — conservative, visible, requires review
    MALFORMED = "MALFORMED"   # Could not parse permission structure


class RepositorySelection(str, Enum):
    ALL = "all"
    SELECTED = "selected"
    NONE = "none"


@dataclass
class NormalizedPermission:
    """A single permission, carrying both the raw provider value and the canonical mapping."""
    raw_provider_key: str           # e.g. "contents"
    raw_provider_value: str         # e.g. "write"
    canonical_permission: CanonicalPermission
    normalization_status: NormalizationStatus
    normalization_version: str = "1.0.0"
    severity: str = "MEDIUM"        # CRITICAL, HIGH, MEDIUM, LOW, INFO
    notes: Optional[str] = None


@dataclass
class NormalizedRepository:
    """Normalized representation of a provider repository/resource."""
    external_id: str
    name: str
    full_name: str
    owner: str
    is_private: bool
    is_fork: bool
    default_branch: str
    description: Optional[str]
    visibility: str                  # public, private, internal
    classification: str = "UNCLASSIFIED"   # UNCLASSIFIED, INTERNAL, SENSITIVE, CRITICAL_SOURCE_CODE, CROWN_JEWEL
    raw_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NormalizedInstallation:
    """Normalized representation of a GitHub App installation."""
    installation_id: str
    account_login: str
    account_type: str               # Organization, User
    app_id: str
    app_slug: str
    repository_selection: RepositorySelection
    permissions: List[NormalizedPermission] = field(default_factory=list)
    repositories: List[NormalizedRepository] = field(default_factory=list)
    is_suspended: bool = False
    suspension_reason: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    raw_evidence_id: Optional[str] = None


@dataclass
class ConnectorHealth:
    """Current health state of a connector."""
    status: str       # HEALTHY, DEGRADED, STALE, AUTH_FAILED, RATE_LIMITED, UNAVAILABLE, MISCONFIGURED
    last_sync_at: Optional[datetime]
    last_attempted_at: Optional[datetime]
    last_error: Optional[str]
    apps_discovered: int
    permissions_discovered: int
    data_freshness_seconds: Optional[int]
    rate_limit_reset_at: Optional[datetime] = None


@dataclass
class SyncResult:
    """Result of a completed connector sync run."""
    connector_id: str
    status: str
    records_collected: int
    records_normalized: int
    findings_created: int
    snapshot_id: Optional[str]
    error_message: Optional[str]
    duration_seconds: int
    installations: List[NormalizedInstallation] = field(default_factory=list)
