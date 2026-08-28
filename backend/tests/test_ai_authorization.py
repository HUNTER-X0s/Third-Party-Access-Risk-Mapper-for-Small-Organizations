"""
test_ai_authorization.py
Tests RBAC authorization and endpoint protection for AI Security Analyst API.
"""
import pytest


def test_ai_status_endpoint(client, db_session):
    """Authenticated or demo user can query AI status endpoint."""
    res = client.get("/api/v1/ai/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "AVAILABLE"
    assert data["read_only"] is True


def test_authenticated_viewer_can_query_ai(client, db_session):
    """Authenticated VIEWER role can query AI Analyst endpoint."""
    login = client.post("/api/v1/auth/login", json={
        "email": "viewer@anurag.tech", "password": "DemoPass123!"
    })
    token = login.cookies.get("access_token")
    res = client.post("/api/v1/ai/analyze", json={
        "question": "Provide a high level security summary.",
        "context_type": "GENERAL"
    }, cookies={"access_token": token})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "summary" in data


def test_security_admin_can_query_ai(client, db_session):
    """Authenticated SECURITY_ADMIN can query AI Analyst endpoint."""
    login = client.post("/api/v1/auth/login", json={
        "email": "admin@anurag.tech", "password": "DemoPass123!"
    })
    token = login.cookies.get("access_token")
    res = client.post("/api/v1/ai/analyze", json={
        "question": "Why is GitHub critical?",
        "context_type": "GENERAL"
    }, cookies={"access_token": token})
    assert res.status_code == 200
    assert "answer" in res.json()
