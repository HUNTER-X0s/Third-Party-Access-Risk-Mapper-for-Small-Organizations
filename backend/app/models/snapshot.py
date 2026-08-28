from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base, generate_uuid, utc_now

class SecuritySnapshot(Base):
    __tablename__ = "security_snapshots"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now, nullable=False, index=True)
    snapshot_label = Column(String(100), nullable=False)
    trigger_reason = Column(String(255), default="MANUAL_SNAPSHOT")
    
    security_posture_score = Column(Float, nullable=False)
    total_applications = Column(Integer, default=0)
    critical_findings_count = Column(Integer, default=0)
    high_findings_count = Column(Integer, default=0)
    excess_permissions_count = Column(Integer, default=0)
    crown_jewels_exposed_count = Column(Integer, default=0)
    
    risk_engine_version = Column(String(20), default="v1.5.0")
    state_manifest_json = Column(JSON, nullable=False) # Lightweight reference dictionary of apps, scopes, findings
