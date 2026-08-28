from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import datetime

class RiskFactorOut(BaseModel):
    id: str
    name: str
    category: str
    weight: float
    current_value: float
    normalized_value: float
    explanation: str

    model_config = ConfigDict(from_attributes=True, extra="forbid")

class RemediationOut(BaseModel):
    id: str
    finding_id: str
    action_type: str
    title: str
    description: str
    current_state: str
    target_state: str
    estimated_risk_reduction: float
    simulated_target_score: float
    priority: str
    effort_level: str
    is_simulation: bool
    status: str

    model_config = ConfigDict(from_attributes=True, extra="forbid")

class RiskFindingOut(BaseModel):
    id: str
    organization_id: str
    application_instance_id: str
    finding_type: str
    title: str
    description: str
    severity: str
    risk_score_contribution: float
    risk_engine_version: str
    lifecycle_state: str
    confidence: str
    affected_application_name: str
    affected_data_name: Optional[str] = None
    business_impact: Optional[str] = None
    created_at: datetime
    factors: List[RiskFactorOut] = []
    remediations: List[RemediationOut] = []

    model_config = ConfigDict(from_attributes=True, extra="forbid")

class SimulationRequest(BaseModel):
    revoked_scopes: List[str]

    model_config = ConfigDict(extra="forbid")

class SimulationResponse(BaseModel):
    is_simulation: bool = True
    mode_label: str = "SIMULATION ONLY"
    current_score: float
    current_severity: str
    simulated_score: float
    simulated_severity: str
    risk_reduction_delta: float
    percentage_reduction: float
    revoked_scopes_count: int
    simulated_result: Any

    model_config = ConfigDict(extra="forbid")
