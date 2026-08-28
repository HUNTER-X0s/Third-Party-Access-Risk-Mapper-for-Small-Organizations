from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base, generate_uuid, utc_now

class EvidenceSource(Base):
    __tablename__ = "evidence_sources"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    connector_type = Column(String(100), default="DEMO_SEED")  # GOOGLE_WORKSPACE, MS_365, MANUAL_AUDIT, DEMO_SEED
    connector_instance_id = Column(String(100), nullable=True)
    api_endpoint = Column(String(255), default="demo://audit/oauth_grants")
    authenticated_identity = Column(String(255), default="admin@anurag.tech")
    trust_level = Column(String(50), default="VERIFIED_API")  # VERIFIED_API, UNVERIFIED_IMPORT, MANUAL_ENTRY
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    # Relationships
    raw_evidences = relationship("RawEvidence", back_populates="evidence_source")

class RawEvidence(Base):
    __tablename__ = "raw_evidences"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    evidence_source_id = Column(String(36), ForeignKey("evidence_sources.id"), nullable=False)
    
    payload_hash_sha256 = Column(String(64), nullable=False)  # Tamper-evident integrity hash
    raw_payload_json = Column(JSON, nullable=False)  # Raw snapshot payload
    collected_at = Column(DateTime(timezone=True), default=utc_now)
    data_freshness_status = Column(String(20), default="CONFIRMED")  # CONFIRMED, STALE, CONFLICTING
    
    # Relationships
    evidence_source = relationship("EvidenceSource", back_populates="raw_evidences")
    finding_links = relationship("FindingEvidenceLink", back_populates="raw_evidence")
    security_facts = relationship("SecurityFact", back_populates="raw_evidence")

class FindingEvidenceLink(Base):
    __tablename__ = "finding_evidence_links"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    finding_id = Column(String(36), ForeignKey("risk_findings.id"), nullable=False, index=True)
    raw_evidence_id = Column(String(36), ForeignKey("raw_evidences.id"), nullable=False, index=True)
    confidence_score = Column(Float, default=1.0)  # 0.0 to 1.0
    
    # Relationships
    finding = relationship("RiskFinding", back_populates="evidence_links")
    raw_evidence = relationship("RawEvidence", back_populates="finding_links")

class SecurityFact(Base):
    __tablename__ = "security_facts"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    raw_evidence_id = Column(String(36), ForeignKey("raw_evidences.id"), nullable=False)
    
    fact_type = Column(String(100), nullable=False)  # PERMISSION_GRANTED, DATA_ACCESS, APPLICATION_APPROVED, BUSINESS_PURPOSE_DECLARED
    subject_entity = Column(String(255), nullable=False)
    fact_details = Column(JSON, nullable=False)
    observed_at = Column(DateTime(timezone=True), default=utc_now)
    
    # Relationships
    raw_evidence = relationship("RawEvidence", back_populates="security_facts")
