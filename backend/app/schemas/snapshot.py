from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime

class SecuritySnapshotCreate(BaseModel):
    snapshot_label: str
    trigger_reason: Optional[str] = "MANUAL_SNAPSHOT"

class SecuritySnapshotOut(BaseModel):
    id: str
    organization_id: str
    created_at: datetime
    snapshot_label: str
    trigger_reason: str
    security_posture_score: float
    total_applications: int
    critical_findings_count: int
    high_findings_count: int
    excess_permissions_count: int
    crown_jewels_exposed_count: int
    risk_engine_version: str

    model_config = ConfigDict(from_attributes=True)

class RiskChangeItem(BaseModel):
    category: str
    change_type: str # ADDED, REMOVED, MODIFIED
    description: str
    risk_score_delta: float

class SnapshotComparisonResponse(BaseModel):
    snapshot_a_id: str
    snapshot_b_id: str
    snapshot_a_label: str
    snapshot_b_label: str
    date_a: datetime
    date_b: datetime
    
    score_a: float
    score_b: float
    score_delta: float
    direction: str # ESCALATED, IMPROVED, UNCHANGED
    
    primary_causes: List[RiskChangeItem]
    new_critical_findings: List[str]
    resolved_critical_findings: List[str]
    new_attack_paths_count: int
    removed_attack_paths_count: int
    crown_jewel_exposure_changed: bool
