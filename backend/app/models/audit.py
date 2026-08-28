from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base, generate_uuid, utc_now

class AuditEvent(Base):
    __tablename__ = "audit_events"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    
    actor_email = Column(String(255), default="system@anurag.tech")
    action = Column(String(100), nullable=False)  # SEED_IMPORTED, FINDING_CREATED, SIMULATION_EXECUTED, REMEDIATION_PLANNED
    target_type = Column(String(100), nullable=False)  # ApplicationInstance, RiskFinding, Remediation
    target_id = Column(String(36), nullable=False)
    outcome = Column(String(50), default="SUCCESS")
    
    event_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    # Relationships
    organization = relationship("Organization", back_populates="audit_events")
