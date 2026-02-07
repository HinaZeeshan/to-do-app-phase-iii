"""Integration tests for token refresh flow."""

import pytest
from fastapi.testclient import TestClient
from src.main import app
import uuid

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_refresh_flow(client):
    """Test full refresh token lifecycle: signup -> get tokens -> refresh -> rotate -> reuse fail."""
    email = f"test_refresh_{uuid.uuid4()}@example.com"
    password = "Password123"

    # 1. Signup
    response = client.post("/api/auth/signup", json={"email": email, "password": password})
    assert response.status_code == 201
    data = response.json()
    assert "token" in data
    assert "refresh_token" in data
    
    refresh_token = data["refresh_token"]
    first_access_token = data["token"]
    
    # 2. Refresh
    response = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    if response.status_code != 200:
        print(f"Refresh failed: {response.json()}")
    assert response.status_code == 200
    new_data = response.json()
    assert "access_token" in new_data
    assert "refresh_token" in new_data
    
    # Verify tokens changed
    assert new_data["access_token"] != first_access_token
    assert new_data["refresh_token"] != refresh_token
    
    new_refresh_token = new_data["refresh_token"]

    # 3. Verify old refresh token fails (Rotation)
    response = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Invalid refresh token"
    
    # 4. Verify new refresh token works
    response = client.post("/api/auth/refresh", json={"refresh_token": new_refresh_token})
    assert response.status_code == 200
