"""
app/models/monitoring.py
Database models for Phase 7 Continuous Monitoring, Security Changes, Incidents, and Application Baselines.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base, generate_uuid, utc_now


class SecurityChange(Base):
    """
    Deterministic record of an observed security state change between two trusted snapshots.
    """
    __tablename__ = "security_changes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    snapshot_before_id = Column(String(36), ForeignKey("security_snapshots.id"), nullable=True)
    snapshot_after_id = Column(String(36), ForeignKey("security_snapshots.id"), nullable=False)

    change_type = Column(String(100), nullable=False)  # PERMISSION_ESCALATED, PERMISSION_REDUCED, SHADOW_SAAS_DETECTED, CROWN_JEWEL_REACHABILITY_CREATED, etc.
    object_type = Column(String(50), nullable=False)   # APPLICATION, PERMISSION, DATA_ASSET, FINDING, PATH
    object_id = Column(String(100), nullable=False)
    object_name = Column(String(255), nullable=True)

    timestamp = Column(DateTime(timezone=True), default=utc_now, index=True)
    source = Column(String(100), default="CONNECTOR_SYNC")
    severity = Column(String(20), default="Medium")     # Critical, High, Medium, Low, Info
    confidence = Column(String(20), default="HIGH")       # VERIFIED, HIGH, MEDIUM, LOW

    evidence_refs = Column(JSON, default=list)            # List of before/after evidence IDs
    impact_summary = Column(Text, nullable=True)
    status = Column(String(50), default="NEW")            # NEW, REVIEWED, ACKNOWLEDGED, RESOLVED

    # Relationships
    organization = relationship("Organization")
    snapshot_before = relationship("SecuritySnapshot", foreign_keys=[snapshot_before_id])
    snapshot_after = relationship("SecuritySnapshot", foreign_keys=[snapshot_after_id])


class SecurityIncident(Base):
    """
    Correlated security event grouping multiple related changes from one synchronization run.
    """
    __tablename__ = "security_incidents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)

    detected_at = Column(DateTime(timezone=True), default=utc_now, index=True)
    source = Column(String(100), default="CONNECTOR_SYNC")
    severity = Column(String(20), default="High")
    summary = Column(Text, nullable=False)

    change_ids = Column(JSON, default=list)              # List of SecurityChange UUIDs
    risk_before = Column(Float, default=0.0)
    risk_after = Column(Float, default=0.0)
    risk_delta = Column(Float, default=0.0)

    blast_radius_before = Column(Float, default=0.0)
    blast_radius_after = Column(Float, default=0.0)
    attack_paths_before = Column(JSON, default=list)
    attack_paths_after = Column(JSON, default=list)

    status = Column(String(50), default="OPEN")          # OPEN, ACKNOWLEDGED, INVESTIGATING, MITIGATED, RESOLVED, DISMISSED
    evidence_refs = Column(JSON, default=list)

    # Relationships
    organization = relationship("Organization")


class ApplicationBaseline(Base):
    """
    Approved access baseline and lifecycle observation metadata for Shadow SaaS detection.
    """
    __tablename__ = "application_baselines"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    application_instance_id = Column(String(36), ForeignKey("application_instances.id"), nullable=False, index=True)

    approved_permissions = Column(JSON, default=list)     # List of canonical permission strings
    approved_data_categories = Column(JSON, default=list)
    is_approved = Column(Boolean, default=False)
    approval_status = Column(String(50), default="UNAPPROVED")  # APPROVED, UNAPPROVED, REVIEW_REQUIRED, RESTRICTED, REJECTED

    approved_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    first_seen_at = Column(DateTime(timezone=True), default=utc_now)
    last_seen_at = Column(DateTime(timezone=True), default=utc_now)

    # Relationships
    organization = relationship("Organization")
    application_instance = relationship("ApplicationInstance")
    approved_by_user = relationship("User")


class SecurityNotification(Base):
    """
    In-app notification generated from SecurityChange or SecurityIncident.
    Deduplicated via stable fingerprint to prevent alert fatigue.
    """
    __tablename__ = "security_notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)

    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=True)
    severity = Column(String(20), default="Medium")   # Critical, High, Medium, Low, Info

    # Notification classification
    notification_type = Column(String(100), nullable=False)  # CRITICAL_PERMISSION_ESCALATION, HIGH_SHADOW_SAAS, etc.
    source_type = Column(String(50), default="CHANGE")        # CHANGE, INCIDENT, CONNECTOR
    source_id = Column(String(36), nullable=True)             # ID of the generating SecurityChange/Incident

    # Deduplication
    fingerprint = Column(String(64), nullable=False, index=True)  # SHA-256 hex of (org_id + type + source_id)

    # Read state
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)

    # Relationships
    organization = relationship("Organization")

