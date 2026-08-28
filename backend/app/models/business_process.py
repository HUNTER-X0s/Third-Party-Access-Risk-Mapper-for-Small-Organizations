from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base, generate_uuid, utc_now

class Department(Base):
    __tablename__ = "departments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False)
    user_count = Column(Integer, default=1)
    head_email = Column(String(255), nullable=True)

class BusinessProcess(Base):
    __tablename__ = "business_processes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(String(500), nullable=True)
    criticality = Column(Integer, default=3) # 1 (Low) to 5 (Critical)
    owner_department = Column(String(100), nullable=True)
