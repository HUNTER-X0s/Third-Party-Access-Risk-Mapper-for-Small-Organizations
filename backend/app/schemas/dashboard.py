from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any
from app.schemas.finding import RiskFindingOut
from app.schemas.application import ApplicationInstanceOut

class DashboardSummaryOut(BaseModel):
    organization_name: str
    security_posture_score: float
    total_applications: int
    active_applications: int
    shadow_applications: int
    dormant_applications: int
    critical_findings_count: int
    high_findings_count: int
    total_excess_permissions: int
    sensitive_data_assets_count: int
    data_freshness_status: str = "CONFIRMED"
    risk_distribution: Dict[str, int]
    top_findings: List[RiskFindingOut]
    applications: List[ApplicationInstanceOut]

    model_config = ConfigDict(extra="forbid")
