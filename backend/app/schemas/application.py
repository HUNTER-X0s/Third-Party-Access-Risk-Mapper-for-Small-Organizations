from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class VendorOut(BaseModel):
    id: str
    name: str
    website: Optional[str] = None
    soc2_status: str
    iso27001_certified: bool
    known_breach_history: bool
    trust_score: float

    model_config = ConfigDict(from_attributes=True, extra="forbid")

class ApplicationOut(BaseModel):
    id: str
    canonical_name: str
    category: str
    provider_type: str
    description: Optional[str] = None
    vendor: Optional[VendorOut] = None

    model_config = ConfigDict(from_attributes=True, extra="forbid")

class ApplicationInstanceOut(BaseModel):
    id: str
    organization_id: str
    display_name: str
    status: str
    authorized_by_email: str
    authorized_at: datetime
    last_activity_at: datetime
    is_shadow: bool
    approved_by_admin: bool
    risk_score: float
    risk_severity: str
    technical_risk_score: float
    data_exposure_risk_score: float
    business_impact_risk_score: float
    vendor_risk_score: float
    attack_path_risk_score: float
    application: ApplicationOut

    model_config = ConfigDict(from_attributes=True, extra="forbid")
