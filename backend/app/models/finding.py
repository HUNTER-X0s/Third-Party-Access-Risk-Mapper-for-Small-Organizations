from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base, generate_uuid, utc_now

class RiskFinding(Base):
    __tablename__ = "risk_findings"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    application_instance_id = Column(String(36), ForeignKey("application_instances.id"), nullable=False, index=True)
    
    finding_type = Column(String(100), nullable=False)  # EXCESS_PERMISSION, PURPOSE_DATA_MISMATCH, SHADOW_APP, STALE_ACCESS
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), default="High")  # Critical, High, Medium, Low
    risk_score_contribution = Column(Float, default=25.0)
    risk_engine_version = Column(String(20), default="v1.5.0")
    lifecycle_state = Column(String(50), default="NEW")  # NEW, TRIAGED, ACKNOWLEDGED, REMEDIATION_PLANNED, APPROVAL_REQUIRED, REMEDIATION_IN_PROGRESS, VERIFIED, CLOSED
    confidence = Column(String(20), default="HIGH")  # HIGH, MEDIUM, LOW
    
    affected_application_name = Column(String(255), nullable=False)
    affected_data_name = Column(String(255), nullable=True)
    business_impact = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now)
    
    # Relationships
    organization = relationship("Organization", back_populates="findings")
    application_instance = relationship("ApplicationInstance", back_populates="findings")
    evidence_links = relationship("FindingEvidenceLink", back_populates="finding", cascade="all, delete-orphan")
    factors = relationship("RiskFactor", back_populates="finding", cascade="all, delete-orphan")
    remediations = relationship("Remediation", back_populates="finding", cascade="all, delete-orphan")

class RiskFactor(Base):
    __tablename__ = "risk_factors"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    finding_id = Column(String(36), ForeignKey("risk_findings.id"), nullable=False, index=True)
    
    name = Column(String(100), nullable=False)  # Technical Risk, Data Exposure, Excess Privilege, Vendor Trust, etc.
    category = Column(String(50), default="PERMISSION")
    weight = Column(Float, default=0.20)
    current_value = Column(Float, default=50.0)
    normalized_value = Column(Float, default=10.0)
    explanation = Column(Text, nullable=False)
    
    # Relationships
    finding = relationship("RiskFinding", back_populates="factors")

class Remediation(Base):
    __tablename__ = "remediations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    finding_id = Column(String(36), ForeignKey("risk_findings.id"), nullable=False, index=True)
    
    action_type = Column(String(100), default="REVOKE_EXCESS_SCOPE")  # REVOKE_EXCESS_SCOPE, REVOKE_APP, REVIEW_ACCESS
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    current_state = Column(String(255), nullable=False)
    target_state = Column(String(255), nullable=False)
    
    estimated_risk_reduction = Column(Float, default=40.0)
    simulated_target_score = Column(Float, default=30.0)
    priority = Column(String(20), default="High")  # Critical, High, Medium, Low
    effort_level = Column(String(20), default="Low")  # Low, Medium, High
    is_simulation = Column(Boolean, default=True)  # True for simulation mode
    
    status = Column(String(50), default="PENDING")  # PENDING, SIMULATED, APPROVED, EXECUTED
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    # Relationships
    finding = relationship("RiskFinding", back_populates="remediations")
