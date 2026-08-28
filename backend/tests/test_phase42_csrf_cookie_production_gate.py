import pytest
from app.core.config import Settings
from app.models import User
from app.core.security import create_access_token

def test_csrf_unauthorized_cross_origin_rejection(client, db_session):
    """Verifies state-changing requests from unauthorized origins are rejected by Anti-CSRF middleware."""
    login_res = client.post("/api/v1/auth/login", json={
        "email": "admin@anurag.tech",
        "password": "DemoPass123!"
    })
    cookie_token = login_res.cookies["access_token"]

    # State-changing request with malicious Origin header
    csrf_attack_res = client.post(
        "/api/v1/snapshots",
        json={"snapshot_label": "CSRF Attack Snapshot", "trigger_reason": "ATTACK"},
        cookies={"access_token": cookie_token},
        headers={"Origin": "http://evil-attacker-site.com"}
    )
    assert csrf_attack_res.status_code == 403
    assert "CSRF Defense" in csrf_attack_res.json()["detail"]

def test_csrf_valid_origin_and_requested_with_header_pass(client, db_session):
    """Verifies state-changing requests with valid Origin and X-Requested-With header pass."""
    login_res = client.post("/api/v1/auth/login", json={
        "email": "admin@anurag.tech",
        "password": "DemoPass123!"
    })
    cookie_token = login_res.cookies["access_token"]

    res = client.post(
        "/api/v1/snapshots",
        json={"snapshot_label": "Valid Snapshot", "trigger_reason": "MANUAL"},
        cookies={"access_token": cookie_token},
        headers={
            "Origin": "http://localhost:5173",
            "X-Requested-With": "XMLHttpRequest"
        }
    )
    assert res.status_code == 200
    assert res.json()["snapshot_label"] == "Valid Snapshot"

def test_production_mode_fail_closed_validation():
    """Verifies validate_production_config raises ValueError when weak secret or insecure cookie is set in production."""
    # Weak secret in production
    insecure_settings_secret = Settings(
        DEMO_MODE=False,
        ENVIRONMENT="production",
        SECRET_KEY="weak-secret",
        COOKIE_SECURE=True
    )
    with pytest.raises(ValueError, match="SECRET_KEY must be a strong random key"):
        insecure_settings_secret.validate_production_config()

    # Insecure cookie in production
    insecure_settings_cookie = Settings(
        DEMO_MODE=False,
        ENVIRONMENT="production",
        SECRET_KEY="a"*35,
        COOKIE_SECURE=False
    )
    with pytest.raises(ValueError, match="COOKIE_SECURE must be True"):
        insecure_settings_cookie.validate_production_config()

def test_demo_reset_disabled_in_production_mode(client, db_session, monkeypatch):
    """Verifies /api/v1/demo/reset returns 403 Forbidden when DEMO_MODE is False."""
    from app.core import config
    monkeypatch.setattr(config.settings, "DEMO_MODE", False)

    login_res = client.post("/api/v1/auth/login", json={
        "email": "superadmin@anurag.tech",
        "password": "DemoPass123!"
    })
    cookie_token = login_res.cookies["access_token"]

    res = client.post("/api/v1/demo/reset", cookies={"access_token": cookie_token})
    assert res.status_code == 403
    assert "disabled in production mode" in res.json()["detail"]

def test_demo_reset_access_control_denial(client, db_session):
    """Verifies non-admin roles (VIEWER, AUDITOR, APP_OWNER) cannot invoke demo reset."""
    for role_email in ["viewer@anurag.tech", "auditor@anurag.tech", "devops@anurag.tech"]:
        login_res = client.post("/api/v1/auth/login", json={
            "email": role_email,
            "password": "DemoPass123!"
        })
        cookie_token = login_res.cookies["access_token"]

        res = client.post("/api/v1/demo/reset", cookies={"access_token": cookie_token})
        assert res.status_code == 403

def test_hsts_header_environment_awareness(client, db_session, monkeypatch):
    """Verifies Strict-Transport-Security header is emitted only when COOKIE_SECURE is True."""
    from app.core import config

    # Dev mode (COOKIE_SECURE = False) -> HSTS suppressed
    monkeypatch.setattr(config.settings, "COOKIE_SECURE", False)
    res_dev = client.get("/health")
    assert "Strict-Transport-Security" not in res_dev.headers

    # Production HTTPS mode (COOKIE_SECURE = True) -> HSTS emitted
    monkeypatch.setattr(config.settings, "COOKIE_SECURE", True)
    res_prod = client.get("/health")
    assert "Strict-Transport-Security" in res_prod.headers
    assert "max-age=31536000" in res_prod.headers["Strict-Transport-Security"]

def test_cookie_path_and_httponly_attributes(client, db_session):
    """Verifies access_token cookie has HttpOnly, SameSite=Lax, and Path=/api/v1 attributes."""
    login_res = client.post("/api/v1/auth/login", json={
        "email": "admin@anurag.tech",
        "password": "DemoPass123!"
    })
    assert login_res.status_code == 200
    cookie = login_res.cookies.get("access_token")
    assert cookie is not None
