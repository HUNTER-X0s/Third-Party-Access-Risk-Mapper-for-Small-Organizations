from sqlalchemy import Column, String, DateTime, Float, Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base, generate_uuid, utc_now

class Vendor(Base):
    __tablename__ = "vendors"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    website = Column(String(255), nullable=True)
    soc2_status = Column(String(50), default="unknown")  # type1, type2, none, unknown
    iso27001_certified = Column(Boolean, default=False)
    known_breach_history = Column(Boolean, default=False)
    breach_details = Column(Text, nullable=True)
    trust_score = Column(Float, default=70.0)  # 0 to 100
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    # Relationships
    applications = relationship("Application", back_populates="vendor")

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    vendor_id = Column(String(36), ForeignKey("vendors.id"), nullable=True)
    canonical_name = Column(String(255), nullable=False)
    category = Column(String(100), default="Productivity")  # Productivity, Dev, CRM, Marketing, Communication
    provider_type = Column(String(50), default="oauth2")  # google, microsoft, github, slack, oauth2
    description = Column(Text, nullable=True)
    logo_url = Column(String(255), nullable=True)
    
    # Relationships
    vendor = relationship("Vendor", back_populates="applications")
    instances = relationship("ApplicationInstance", back_populates="application")

class ApplicationInstance(Base):
    __tablename__ = "application_instances"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False)
    
    display_name = Column(String(255), nullable=False)
    status = Column(String(50), default="active")  # active, dormant, shadow, revoked
    authorized_by_email = Column(String(255), nullable=False)
    authorized_at = Column(DateTime(timezone=True), default=utc_now)
    last_activity_at = Column(DateTime(timezone=True), default=utc_now)
    is_shadow = Column(Boolean, default=False)
    approved_by_admin = Column(Boolean, default=True)
    
    # Computed Risk Scores
    risk_score = Column(Float, default=50.0)  # Overall 0-100
    risk_severity = Column(String(20), default="Medium")  # Critical, High, Medium, Low, Info
    
    # Dimensional Scores
    technical_risk_score = Column(Float, default=50.0)
    data_exposure_risk_score = Column(Float, default=50.0)
    business_impact_risk_score = Column(Float, default=50.0)
    vendor_risk_score = Column(Float, default=50.0)
    attack_path_risk_score = Column(Float, default=50.0)
    
    risk_last_calculated_at = Column(DateTime(timezone=True), default=utc_now)
    
    # Relationships
    organization = relationship("Organization", back_populates="applications")
    application = relationship("Application", back_populates="instances")
    permission_grants = relationship("PermissionGrant", back_populates="application_instance", cascade="all, delete-orphan")
    instance_purposes = relationship("ApplicationInstancePurpose", back_populates="application_instance", cascade="all, delete-orphan")
    access_relationships = relationship("AccessRelationship", back_populates="application_instance", cascade="all, delete-orphan")
    findings = relationship("RiskFinding", back_populates="application_instance", cascade="all, delete-orphan")
