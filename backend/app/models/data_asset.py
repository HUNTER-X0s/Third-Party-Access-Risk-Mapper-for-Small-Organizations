from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base, generate_uuid, utc_now

class DataClassification(Base):
    __tablename__ = "data_classifications"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False, unique=True)  # PII, Financial, Intellectual Property, Operational, Public
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    sensitivity_level = Column(Integer, default=3)  # 1 to 5
    color_code = Column(String(20), default="#facc15")
    
    # Relationships
    data_assets = relationship("DataAsset", back_populates="classification")

class DataAsset(Base):
    __tablename__ = "data_assets"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    classification_id = Column(String(36), ForeignKey("data_classifications.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    system_of_record = Column(String(255), nullable=False)  # GitHub, Google Drive, Slack, etc.
    is_crown_jewel = Column(Boolean, default=False)
    owner_email = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    # Relationships
    organization = relationship("Organization", back_populates="data_assets")
    classification = relationship("DataClassification", back_populates="data_assets")
    access_relationships = relationship("AccessRelationship", back_populates="data_asset", cascade="all, delete-orphan")

class AccessRelationship(Base):
    __tablename__ = "access_relationships"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    application_instance_id = Column(String(36), ForeignKey("application_instances.id"), nullable=False, index=True)
    data_asset_id = Column(String(36), ForeignKey("data_assets.id"), nullable=False, index=True)
    
    access_type = Column(String(50), default="READ")  # READ, WRITE, DELETE, EXPORT, ADMIN
    is_direct = Column(Boolean, default=True)
    last_verified_at = Column(DateTime(timezone=True), default=utc_now)
    
    # Relationships
    application_instance = relationship("ApplicationInstance", back_populates="access_relationships")
    data_asset = relationship("DataAsset", back_populates="access_relationships")
