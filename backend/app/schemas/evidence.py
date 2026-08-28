from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime

class RawEvidenceOut(BaseModel):
    id: str
    organization_id: str
    payload_hash_sha256: str
    raw_payload_json: Any
    collected_at: datetime
    data_freshness_status: str

    model_config = ConfigDict(from_attributes=True, extra="forbid")
