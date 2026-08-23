import pytest
import os
import json
from fastapi.testclient import TestClient

# Set VERCEL environment simulation
os.environ["VERCEL"] = "1"

from server import app, hash_password, load_users, create_access_token

client = TestClient(app)

def test_user_login_success():
    response = client.post("/api/auth/login", json={
        "email": "user@prodexa.com",
        "password": "user123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "access_token" in data
    assert data.get("token_type") == "bearer"
    assert data.get("user", {}).get("role") == "USER"
    assert data.get("user", {}).get("email") == "user@prodexa.com"

def test_admin_login_success():
    response = client.post("/api/auth/login", json={
        "email": "admin@prodexa.com",
        "password": "admin123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "access_token" in data
    assert data.get("user", {}).get("role") == "ADMIN"
    assert data.get("user", {}).get("email") == "admin@prodexa.com"

def test_login_invalid_password():
    response = client.post("/api/auth/login", json={
        "email": "user@prodexa.com",
        "password": "wrongpassword999"
    })
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data or "error" in data

def test_login_missing_fields():
    response = client.post("/api/auth/login", json={
        "email": "",
        "password": ""
    })
    assert response.status_code == 400

def test_auth_me_endpoint():
    # 1. Login to get token
    login_res = client.post("/api/auth/login", json={
        "email": "user@prodexa.com",
        "password": "user123"
    })
    token = login_res.json()["access_token"]

    # 2. Call /api/auth/me with Bearer token
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data.get("email") == "user@prodexa.com"
    assert me_data.get("role") == "USER"

def test_serverless_entrypoint_import():
    # Verify api/index.py imports cleanly without raising exceptions
    import api.index as serverless_entry
    assert serverless_entry.app is not None
