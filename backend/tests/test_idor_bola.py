import pytest
from app.models import Organization, ApplicationInstance, RiskFinding, User
from app.core.security import get_password_hash, create_access_token

def test_idor_bola_cross_tenant_application_denial(client, db_session):
    """
    Verifies that a user from Organization B attempting to fetch an application ID
    belonging to Organization A receives a 404 Not Found (BOLA protection).
    """
    # Create Organization B
    org_b = Organization(name="Org B Competitor", domain="competitor.org", security_posture_score=80.0)
    db_session.add(org_b)
    db_session.commit()

    user_b = User(
        organization_id=org_b.id,
        email="attacker@competitor.org",
        display_name="Attacker Org B",
        password_hash=get_password_hash("AttackerPass123!"),
        role="SECURITY_ADMIN",
        status="ACTIVE"
    )
    db_session.add(user_b)
    db_session.commit()

    token_b = create_access_token({"sub": user_b.id, "email": user_b.email, "org_id": org_b.id, "role": user_b.role})
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Fetch GitHub App from Org A (Anurag Technologies)
    gh_app_a = db_session.query(ApplicationInstance).filter(ApplicationInstance.display_name == "GitHub Production Sync").first()
    assert gh_app_a is not None

    # Org B user tries to access Org A's application ID
    res = client.get(f"/api/v1/applications/{gh_app_a.id}", headers=headers_b)
    assert res.status_code == 404
    assert res.json()["detail"] == "Application instance not found"

def test_idor_bola_cross_tenant_finding_denial(client, db_session):
    """
    Verifies that a user from Organization B attempting to fetch or simulate a finding ID
    belonging to Organization A receives a 404 Not Found.
    """
    org_b = db_session.query(Organization).filter(Organization.domain == "competitor.org").first()
    if not org_b:
        org_b = Organization(name="Org B Competitor", domain="competitor.org", security_posture_score=80.0)
        db_session.add(org_b)
        db_session.commit()

    user_b = db_session.query(User).filter(User.email == "attacker@competitor.org").first()
    if not user_b:
        user_b = User(
            organization_id=org_b.id,
            email="attacker@competitor.org",
            display_name="Attacker Org B",
            password_hash=get_password_hash("AttackerPass123!"),
            role="SECURITY_ADMIN",
            status="ACTIVE"
        )
        db_session.add(user_b)
        db_session.commit()

    token_b = create_access_token({"sub": user_b.id, "email": user_b.email, "org_id": org_b.id, "role": user_b.role})
    headers_b = {"Authorization": f"Bearer {token_b}"}

    finding_a = db_session.query(RiskFinding).first()
    assert finding_a is not None

    # Org B user attempts to fetch Org A's finding
    res = client.get(f"/api/v1/findings/{finding_a.id}", headers=headers_b)
    assert res.status_code == 404

    # Org B user attempts to simulate Org A's finding
    res_sim = client.post(f"/api/v1/findings/{finding_a.id}/simulate-remediation", json={"revoked_scopes": ["repo_write"]}, headers=headers_b)
    assert res_sim.status_code == 404
