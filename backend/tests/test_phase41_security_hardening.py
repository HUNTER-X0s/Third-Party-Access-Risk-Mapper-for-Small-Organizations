import pytest
from datetime import datetime, timezone, timedelta
from app.models import User, UserSession, Organization
from app.core.security import create_access_token, get_password_hash

def test_cookie_authentication_transport(client, db_session):
    """Verifies authentication via HttpOnly cookie."""
    login_res = client.post("/api/v1/auth/login", json={
        "email": "admin@anurag.tech",
        "password": "DemoPass123!"
    })
    assert login_res.status_code == 200
    assert "access_token" in login_res.cookies

    # Make request using cookie transport
    cookie_token = login_res.cookies["access_token"]
    res = client.get("/api/v1/auth/me", cookies={"access_token": cookie_token})
    assert res.status_code == 200
    assert res.json()["email"] == "admin@anurag.tech"

def test_account_lockout_after_five_failed_attempts(client, db_session):
    """Verifies account is locked out for 15 minutes after 5 consecutive failed login attempts."""
    email = "admin@anurag.tech"

    # Reset failed login count first
    user = db_session.query(User).filter(User.email == email).first()
    user.failed_login_count = 0
    user.locked_until = None
    db_session.commit()

    for i in range(5):
        res = client.post("/api/v1/auth/login", json={"email": email, "password": "WrongPassword!"})
        assert res.status_code == 401
        assert res.json()["detail"] == "Invalid email or password"

    # 6th attempt when account is locked
    res_locked = client.post("/api/v1/auth/login", json={"email": email, "password": "DemoPass123!"})
    assert res_locked.status_code == 401
    assert res_locked.json()["detail"] == "Invalid email or password"

    # Reset for subsequent tests
    user.failed_login_count = 0
    user.locked_until = None
    db_session.commit()

def test_session_revocation_replay_failure(client, db_session):
    """Verifies that reusing a session token post-logout fails with 401 Unauthorized."""
    login_res = client.post("/api/v1/auth/login", json={
        "email": "admin@anurag.tech",
        "password": "DemoPass123!"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Logout to revoke session
    logout_res = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_res.status_code == 200

    # Attempt to reuse revoked token
    replay_res = client.get("/api/v1/auth/me", headers=headers)
    assert replay_res.status_code == 401
    assert "revoked" in replay_res.json()["detail"].lower()

def test_post_issuance_role_downgrade(client, db_session):
    """Verifies that downgrading a user's role in DB instantly denies protected access for existing tokens."""
    admin_user = db_session.query(User).filter(User.email == "admin@anurag.tech").first()
    token = create_access_token({"sub": admin_user.id, "email": admin_user.email, "org_id": admin_user.organization_id, "role": "SECURITY_ADMIN"})
    headers = {"Authorization": f"Bearer {token}"}

    # Verify admin access before downgrade
    res_before = client.get("/api/v1/users", headers=headers)
    assert res_before.status_code == 200

    # Downgrade role to VIEWER in DB
    admin_user.role = "VIEWER"
    db_session.commit()

    # Attempt admin request with existing token -> must fail 403
    res_after = client.get("/api/v1/users", headers=headers)
    assert res_after.status_code == 403
    assert "lacks permission" in res_after.json()["detail"]

    # Restore role
    admin_user.role = "SECURITY_ADMIN"
    db_session.commit()

def test_post_issuance_user_suspension(client, db_session):
    """Verifies that suspending a user in DB instantly revokes API access for active tokens."""
    user = db_session.query(User).filter(User.email == "auditor@anurag.tech").first()
    token = create_access_token({"sub": user.id, "email": user.email, "org_id": user.organization_id, "role": user.role})
    headers = {"Authorization": f"Bearer {token}"}

    # Suspend user in DB
    user.status = "SUSPENDED"
    db_session.commit()

    res = client.get("/api/v1/auth/me", headers=headers)
    assert res.status_code == 403
    assert "suspended" in res.json()["detail"].lower()

    # Reactivate user
    user.status = "ACTIVE"
    db_session.commit()

def test_invalid_jwt_issuer_rejection(client, db_session):
    """Verifies tokens with invalid issuer claims are rejected."""
    user = db_session.query(User).filter(User.email == "admin@anurag.tech").first()
    bad_issuer_token = create_access_token({
        "sub": user.id,
        "email": user.email,
        "org_id": user.organization_id,
        "role": user.role,
        "iss": "MaliciousAttackerApp"
    })
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {bad_issuer_token}"})
    assert res.status_code == 401
    assert "Invalid token issuer" in res.json()["detail"]

def test_security_headers_presence(client, db_session):
    """Verifies security headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection) on responses."""
    res = client.get("/health")
    assert res.status_code == 200
    assert res.headers["X-Content-Type-Options"] == "nosniff"
    assert res.headers["X-Frame-Options"] == "DENY"
    assert res.headers["X-XSS-Protection"] == "1; mode=block"
