from sqlalchemy import Column, String, DateTime, Float
from sqlalchemy.orm import relationship
from app.db.base_class import Base, generate_uuid, utc_now

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=False, unique=True)
    plan_tier = Column(String(50), default="pro")
    created_at = Column(DateTime(timezone=True), default=utc_now)
    security_posture_score = Column(Float, default=70.0)
    
    # Relationships
    applications = relationship("ApplicationInstance", back_populates="organization", cascade="all, delete-orphan")
    data_assets = relationship("DataAsset", back_populates="organization", cascade="all, delete-orphan")
    findings = relationship("RiskFinding", back_populates="organization", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="organization", cascade="all, delete-orphan")
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    memberships = relationship("OrganizationMembership", back_populates="organization", cascade="all, delete-orphan")
