from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base, generate_uuid, utc_now

class BusinessPurposeCatalog(Base):
    __tablename__ = "business_purpose_catalog"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    purpose_code = Column(String(100), nullable=False, unique=True)  # REPO_COLLABORATION, CUSTOMER_SUPPORT_AUTO, etc.
    display_name = Column(String(255), nullable=False)
    category = Column(String(100), default="Productivity")
    description = Column(Text, nullable=True)
    version = Column(String(20), default="v1.0")
    is_active = Column(Boolean, default=True)
    
    # Relationships
    requirements = relationship("BusinessPurposeRequirement", back_populates="purpose", cascade="all, delete-orphan")
    instance_bindings = relationship("ApplicationInstancePurpose", back_populates="purpose")

class BusinessPurposeRequirement(Base):
    __tablename__ = "business_purpose_requirements"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    purpose_id = Column(String(36), ForeignKey("business_purpose_catalog.id"), nullable=False)
    permission_id = Column(String(36), ForeignKey("permissions.id"), nullable=False)
    requirement_type = Column(String(20), default="MANDATORY")  # MANDATORY, OPTIONAL
    justification_rationale = Column(Text, nullable=True)
    
    # Relationships
    purpose = relationship("BusinessPurposeCatalog", back_populates="requirements")
    permission = relationship("Permission", back_populates="purpose_requirements")

class ApplicationInstancePurpose(Base):
    __tablename__ = "application_instance_purposes"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_instance_id = Column(String(36), ForeignKey("application_instances.id"), nullable=False, index=True)
    purpose_id = Column(String(36), ForeignKey("business_purpose_catalog.id"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), default=utc_now)
    approved_by_email = Column(String(255), nullable=True)
    custom_notes = Column(Text, nullable=True)
    
    # Relationships
    application_instance = relationship("ApplicationInstance", back_populates="instance_purposes")
    purpose = relationship("BusinessPurposeCatalog", back_populates="instance_bindings")
