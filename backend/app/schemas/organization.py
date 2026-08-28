from pydantic import BaseModel, ConfigDict
from datetime import datetime

class OrganizationOut(BaseModel):
    id: str
    name: str
    domain: str
    plan_tier: str
    security_posture_score: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="forbid")
