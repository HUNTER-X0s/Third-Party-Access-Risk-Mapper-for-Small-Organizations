from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class DataClassificationOut(BaseModel):
    id: str
    name: str
    display_name: str
    sensitivity_level: int
    color_code: str

    model_config = ConfigDict(from_attributes=True, extra="forbid")

class DataAssetOut(BaseModel):
    id: str
    organization_id: str
    name: str
    description: Optional[str] = None
    system_of_record: str
    is_crown_jewel: bool
    owner_email: Optional[str] = None
    classification: DataClassificationOut

    model_config = ConfigDict(from_attributes=True, extra="forbid")

class AccessRelationshipOut(BaseModel):
    id: str
    application_instance_id: str
    data_asset_id: str
    access_type: str
    is_direct: bool
    last_verified_at: datetime
    data_asset: DataAssetOut

    model_config = ConfigDict(from_attributes=True, extra="forbid")
