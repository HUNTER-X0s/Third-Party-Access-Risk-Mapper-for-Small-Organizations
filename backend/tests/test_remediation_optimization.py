import pytest
from app.models import Organization, RiskFinding
from app.services.remediation_optimizer import RemediationOptimizer

def test_minimum_effective_remediation(db_session):
    org = db_session.query(Organization).first()
    finding = db_session.query(RiskFinding).filter(RiskFinding.severity == "Critical").first()
    
    optimizer = RemediationOptimizer(db_session, org.id)
    res = optimizer.calculate_minimum_effective_remediation(finding.id, target_max_score=55.0)
    
    assert res["finding_id"] == finding.id
    assert res["predicted_residual_score"] <= 55.0
    assert res["risk_reduction_delta"] > 0
    assert len(res["recommended_minimal_revocations"]) >= 1
    assert res["is_simulation"] is True
