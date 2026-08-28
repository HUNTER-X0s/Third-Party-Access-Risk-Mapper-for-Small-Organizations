from sqlalchemy import Column, String, DateTime, Integer, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base, generate_uuid, utc_now


class ProviderConnector(Base):
    """
    Represents a configured third-party provider connector for an organization.
    Stores non-secret configuration only. Credentials are environment-managed.
    """
    __tablename__ = "provider_connectors"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)

    # Provider identity
    provider = Column(String(50), nullable=False)          # GITHUB, GOOGLE_WORKSPACE, MS365, etc.
    display_name = Column(String(255), nullable=False)
    mode = Column(String(20), default="DEMO")              # LIVE, DEMO

    # Runtime status
    status = Column(String(30), default="MISCONFIGURED")   # HEALTHY, DEGRADED, STALE, AUTH_FAILED, RATE_LIMITED, UNAVAILABLE, MISCONFIGURED
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    last_attempted_sync_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    apps_discovered = Column(Integer, default=0)
    permissions_discovered = Column(Integer, default=0)
    data_freshness_seconds = Column(Integer, nullable=True)  # seconds since last successful sync

    # Non-secret configuration (e.g. app_id, base_url, api_version)
    config_json = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    sync_runs = relationship("ConnectorSyncRun", back_populates="connector", cascade="all, delete-orphan")


class ConnectorSyncRun(Base):
    """
    Audit record for a single connector synchronization run.
    Tracks the full lifecycle: STARTED → COMPLETED / FAILED.
    """
    __tablename__ = "connector_sync_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    connector_id = Column(String(36), ForeignKey("provider_connectors.id"), nullable=False, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    triggered_by = Column(String(36), nullable=True)  # User ID who triggered sync

    status = Column(String(30), default="STARTED")   # STARTED, AUTHENTICATING, COLLECTING, NORMALIZING, ANALYZING, SNAPSHOT_CREATED, COMPLETED, FAILED
    started_at = Column(DateTime(timezone=True), default=utc_now)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    records_collected = Column(Integer, default=0)
    records_normalized = Column(Integer, default=0)
    findings_created = Column(Integer, default=0)
    snapshot_id = Column(String(36), nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    connector = relationship("ProviderConnector", back_populates="sync_runs")
