from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class PermissionOut(BaseModel):
    id: str
    canonical_name: str
    display_name: str
    description: Optional[str] = None
    category: str
    severity_level: str

    model_config = ConfigDict(from_attributes=True, extra="forbid")

class PermissionGrantOut(BaseModel):
    id: str
    application_instance_id: str
    raw_scope: str
    granted_at: datetime
    is_excess: bool
    excess_reason: Optional[str] = None
    permission: PermissionOut

    model_config = ConfigDict(from_attributes=True, extra="forbid")
