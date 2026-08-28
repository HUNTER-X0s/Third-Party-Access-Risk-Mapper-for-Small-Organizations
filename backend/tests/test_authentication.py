import pytest
from app.models import User, Organization
from app.core.security import create_access_token

def test_login_success(client, db_session):
    """Verifies POST /api/v1/auth/login succeeds with valid credentials."""
    res = client.post("/api/v1/auth/login", json={
        "email": "admin@anurag.tech",
        "password": "DemoPass123!"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["email"] == "admin@anurag.tech"
    assert data["role"] == "SECURITY_ADMIN"
    assert data["organization_name"] == "Anurag Technologies"

def test_login_wrong_password(client, db_session):
    """Verifies POST /api/v1/auth/login fails with generic 401 message for wrong password."""
    res = client.post("/api/v1/auth/login", json={
        "email": "admin@anurag.tech",
        "password": "WrongPassword123!"
    })
    assert res.status_code == 401
    assert "Invalid email or password" in res.json()["detail"]

def test_login_nonexistent_user(client, db_session):
    """Verifies POST /api/v1/auth/login fails with generic 401 message for unknown user."""
    res = client.post("/api/v1/auth/login", json={
        "email": "nonexistent@anurag.tech",
        "password": "DemoPass123!"
    })
    assert res.status_code == 401
    assert "Invalid email or password" in res.json()["detail"]

def test_get_current_user_profile(client, db_session):
    """Verifies GET /api/v1/auth/me returns authenticated user profile."""
    # Login to get token
    login_res = client.post("/api/v1/auth/login", json={
        "email": "admin@anurag.tech",
        "password": "DemoPass123!"
    })
    token = login_res.json()["access_token"]

    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    user = res.json()
    assert user["email"] == "admin@anurag.tech"
    assert user["role"] == "SECURITY_ADMIN"

def test_logout(client, db_session):
    """Verifies POST /api/v1/auth/logout logs out authenticated user."""
    login_res = client.post("/api/v1/auth/login", json={
        "email": "admin@anurag.tech",
        "password": "DemoPass123!"
    })
    token = login_res.json()["access_token"]

    res = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["status"] == "SUCCESS"
