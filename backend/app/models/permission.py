from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base, generate_uuid, utc_now

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    canonical_name = Column(String(100), nullable=False, unique=True)  # READ, WRITE, DELETE, EXPORT, SHARE, ADMIN, CONFIGURE
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), default="READ")  # READ, WRITE, ADMIN, EXPORT
    severity_level = Column(String(20), default="Medium")  # Critical, High, Medium, Low
    
    # Relationships
    provider_scopes = relationship("ProviderScope", back_populates="permission")
    grants = relationship("PermissionGrant", back_populates="permission")
    purpose_requirements = relationship("BusinessPurposeRequirement", back_populates="permission")

class ProviderScope(Base):
    __tablename__ = "provider_scopes"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    provider_type = Column(String(50), nullable=False)  # google, microsoft, github, slack, oauth2
    raw_scope = Column(String(255), nullable=False)  # repo, Mail.Read, https://www.googleapis.com/auth/gmail.readonly
    permission_id = Column(String(36), ForeignKey("permissions.id"), nullable=False)
    provider_display_name = Column(String(255), nullable=True)
    
    # Relationships
    permission = relationship("Permission", back_populates="provider_scopes")

class PermissionGrant(Base):
    __tablename__ = "permission_grants"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_instance_id = Column(String(36), ForeignKey("application_instances.id"), nullable=False, index=True)
    permission_id = Column(String(36), ForeignKey("permissions.id"), nullable=False)
    raw_scope = Column(String(255), nullable=False)
    granted_at = Column(DateTime(timezone=True), default=utc_now)
    
    is_excess = Column(Boolean, default=False)
    excess_reason = Column(Text, nullable=True)
    
    # Relationships
    application_instance = relationship("ApplicationInstance", back_populates="permission_grants")
    permission = relationship("Permission", back_populates="grants")
