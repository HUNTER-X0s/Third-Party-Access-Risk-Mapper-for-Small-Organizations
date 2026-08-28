"""
app/models/vendor.py
Database models for Phase 8 Supplier / Vendor Risk Intelligence, C-SCRM Due Diligence,
Supply Chain Tiers, and Subprocessor Mapping aligned with NIST SP 1326 & NIST SP 800-161 Rev. 1.
"""
from sqlalchemy import Column, String, DateTime, Float, Boolean, ForeignKey, Integer, Text, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base, generate_uuid, utc_now


class SupplierProfile(Base):
    """
    Organization-scoped supplier intelligence profile.
    Separates organizational relationship context from global vendor metadata.
    """
    __tablename__ = "supplier_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    vendor_id = Column(String(36), ForeignKey("vendors.id"), nullable=False, index=True)

    # Status & Governance Lifecycle
    status = Column(String(50), default="ACTIVE")  # ACTIVE, UNDER_REVIEW, APPROVED, RESTRICTED, SUSPENDED, OFFBOARDED
    business_criticality = Column(String(20), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL

    service_category = Column(String(100), default="SaaS Platform")
    service_description = Column(Text, nullable=True)
    primary_business_owner = Column(String(255), nullable=True)
    security_owner = Column(String(255), nullable=True)

    # Lifecycle Review Dates
    first_seen_at = Column(DateTime(timezone=True), default=utc_now)
    last_reviewed_at = Column(DateTime(timezone=True), nullable=True)
    next_review_due = Column(DateTime(timezone=True), nullable=True)
    assessment_status = Column(String(50), default="CURRENT")  # CURRENT, DUE_SOON, OVERDUE, STALE, UNKNOWN

    # Calculated Supplier (Posture) Risk vs Access Risk
    supplier_risk_score = Column(Float, default=50.0)  # Posture/Due Diligence Risk (0-100)
    supplier_risk_severity = Column(String(20), default="Medium")
    concentration_score = Column(Float, default=0.0)  # Dependency concentration across processes/assets

    # Tier (1 = Direct Supplier, 2 = Critical Subprocessor, 3 = Infrastructure)
    supply_chain_tier = Column(Integer, default=1)

    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    organization = relationship("Organization")
    vendor = relationship("Vendor")
    due_diligence = relationship("SupplierDueDiligence", back_populates="supplier_profile", uselist=False)
    subprocessors = relationship("SupplierSubprocessor", back_populates="supplier_profile")
    assessment_history = relationship("SupplierAssessmentHistory", back_populates="supplier_profile")


class SupplierDueDiligence(Base):
    """
    Structured C-SCRM due-diligence assessment aligned with NIST SP 1326:
    FOCI, Provenance, Resilience, Foundational Cyber Practices, and Supply Chain Depth.
    """
    __tablename__ = "supplier_due_diligence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    supplier_profile_id = Column(String(36), ForeignKey("supplier_profiles.id"), nullable=False, unique=True, index=True)

    # 1. Foreign Ownership, Control, or Influence (FOCI)
    foci_status = Column(String(50), default="NOT_ASSESSED")  # ASSESSED_NO_CONCERN, POTENTIAL_CONCERN, UNKNOWN, NOT_ASSESSED
    foci_details = Column(Text, nullable=True)
    foci_source = Column(String(100), default="MANUAL_ASSESSMENT")
    foci_confidence = Column(String(20), default="MEDIUM")

    # 2. Provenance
    provenance_status = Column(String(50), default="UNKNOWN")  # ASSESSED, CLAIM, UNKNOWN, DISPUTED
    service_origin_country = Column(String(100), default="United States")
    ownership_country = Column(String(100), default="United States")
    hosting_provider = Column(String(100), default="AWS / US-East")
    provenance_notes = Column(Text, nullable=True)

    # 3. Resilience
    resilience_status = Column(String(50), default="UNKNOWN")  # CURRENT, ASSESSED, GAP, UNKNOWN
    sla_availability_pct = Column(Float, default=99.9)
    backup_recovery_tested = Column(Boolean, default=False)
    bcp_dr_documented = Column(Boolean, default=False)
    resilience_notes = Column(Text, nullable=True)

    # 4. Foundational Cyber Practices
    cyber_practices_status = Column(String(50), default="UNKNOWN")  # STRONG, PARTIAL, MINIMAL, UNKNOWN
    mfa_enforced = Column(Boolean, default=False)
    vuln_mgmt_documented = Column(Boolean, default=False)
    incident_response_tested = Column(Boolean, default=False)
    encryption_in_transit_rest = Column(Boolean, default=True)
    security_contact_email = Column(String(255), nullable=True)
    cyber_practices_notes = Column(Text, nullable=True)

    # 5. Supply Chain Tier & Evidence
    supply_chain_tier = Column(Integer, default=1)
    evidence_refs = Column(JSON, default=list)  # SHA-256 raw evidence anchors
    notes = Column(Text, nullable=True)
    version = Column(Integer, default=1)
    is_synthetic_demo = Column(Boolean, default=True)  # Clearly labels demo data

    last_verified_at = Column(DateTime(timezone=True), default=utc_now)
    reviewed_by = Column(String(255), nullable=True)

    # Relationships
    supplier_profile = relationship("SupplierProfile", back_populates="due_diligence")


class SupplierSubprocessor(Base):
    """
    Subprocessor (4th-party) mapping for supply chain visibility.
    """
    __tablename__ = "supplier_subprocessors"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    supplier_profile_id = Column(String(36), ForeignKey("supplier_profiles.id"), nullable=False, index=True)

    subprocessor_name = Column(String(255), nullable=False)
    service_provided = Column(String(255), nullable=False)
    data_shared_categories = Column(JSON, default=list)  # e.g. ["Telemetry", "User Auth", "Billing"]
    hosting_region = Column(String(100), default="US")
    verification_status = Column(String(50), default="DECLARED")  # DECLARED, VERIFIED, INFERRED
    tier = Column(Integer, default=2)  # Tier 2 (Subprocessor), Tier 3 (Infrastructure)
    evidence_refs = Column(JSON, default=list)

    created_at = Column(DateTime(timezone=True), default=utc_now)

    # Relationships
    supplier_profile = relationship("SupplierProfile", back_populates="subprocessors")


class SupplierAssessmentHistory(Base):
    """
    Immutable versioned audit record of historical supplier assessments.
    """
    __tablename__ = "supplier_assessment_history"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    supplier_profile_id = Column(String(36), ForeignKey("supplier_profiles.id"), nullable=False, index=True)

    version = Column(Integer, nullable=False)
    assessment_snapshot_json = Column(JSON, nullable=False)
    change_summary = Column(Text, nullable=True)
    reviewed_by = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    # Relationships
    supplier_profile = relationship("SupplierProfile", back_populates="assessment_history")
