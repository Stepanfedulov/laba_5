from fastapi.testclient import TestClient
from main import app
import time
import pytest

client = TestClient(app)

# Test data
TEST_USER = {
    "username": "testuser_prod",
    "email": "testuser_prod@example.com",
    "full_name": "Test User Prod",
    "password": "password123"
}

INVALID_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjMiLCJleHAiOjE3Mzk5NTQ2NzZ9.tMKZJzUX_heuhdbVHxWW4-OdiTCXa9AvKbSXkAwmrmw"
VALID_TOKEN = None  # Will be set after successful login

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    # Setup: Create a test user and get valid token
    global VALID_TOKEN
    
    # Register test user
    response = client.post("/register/", json=TEST_USER)
    assert response.status_code == 200
    
    # Login to get valid token
    login_response = client.post(
        "/token",
        data={"username": TEST_USER["username"], "password": TEST_USER["password"]},
    )
    assert login_response.status_code == 200
    VALID_TOKEN = f"Bearer {login_response.json()['access_token']}"
    
    yield  # This is where the testing happens
    
    # Teardown: Clean up test user (if needed)
    # In a real production test, you might want to clean up the test user
    # But for this example, we'll skip it to avoid complexity

# Helper functions
def get_auth_headers(token=None):
    return {"Authorization": token or VALID_TOKEN}

# Basic API tests
def test_read_main():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200

def test_performance():
    """Test API response time"""
    start_time = time.time()
    for _ in range(10):
        client.get("/")
    end_time = time.time()
    assert (end_time - start_time) < 1

# Authentication tests
def test_login_success():
    """Test successful authentication"""
    response = client.post(
        "/token",
        data={"username": TEST_USER["username"], "password": TEST_USER["password"]},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_password():
    """Test authentication with invalid password"""
    response = client.post(
        "/token",
        data={"username": TEST_USER["username"], "password": "wrongpassword"},
    )
    assert response.status_code == 401

# User registration tests
def test_create_user_success():
    """Test successful user creation"""
    user_data = {
        "username": "new_test_user",
        "email": "new_test@example.com",
        "full_name": "New Test User",
        "password": "newpassword123"
    }
    response = client.post("/register/", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]

def test_create_user_missing_fields():
    """Test user creation with missing required fields"""
    response = client.post(
        "/register/",
        json={"username": "incomplete_user"}
    )
    assert response.status_code == 422

def test_duplicate_registration():
    """Test duplicate user registration"""
    response = client.post("/register/", json=TEST_USER)
    assert response.status_code == 400  # Assuming your API returns 400 for duplicates

# User management tests
def test_get_users():
    """Test retrieving user list"""
    response = client.get("/users/", headers=get_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_current_user():
    """Test retrieving current user info"""
    response = client.get("/users/me", headers=get_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert "username" in data
    assert data["username"] == TEST_USER["username"]

def test_update_user():
    """Test updating user information"""
    update_data = {"full_name": "Updated Name"}
    response = client.put(
        "/users/me",
        headers=get_auth_headers(),
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == update_data["full_name"]

def test_delete_user():
    """Test user deletion"""
    # First create a user to delete
    temp_user = {
        "username": "temp_user_to_delete",
        "email": "temp_delete@example.com",
        "password": "temp123"
    }
    create_response = client.post("/register/", json=temp_user)
    assert create_response.status_code == 200
    user_id = create_response.json()["id"]
    
    # Now delete the user
    delete_response = client.delete(
        f"/users/{user_id}",
        headers=get_auth_headers()
    )
    assert delete_response.status_code == 200
    
    # Verify user is deleted
    verify_response = client.get(
        f"/users/{user_id}",
        headers=get_auth_headers()
    )
    assert verify_response.status_code == 404

# Security tests
def test_protected_route_without_token():
    """Test accessing protected route without token"""
    response = client.get("/users/")
    assert response.status_code == 401

def test_protected_route_with_invalid_token():
    """Test accessing protected route with invalid token"""
    response = client.get("/users/", headers=get_auth_headers(INVALID_TOKEN))
    assert response.status_code == 401

# CORS tests
def test_cors_allowed():
    """Test CORS headers"""
    headers = {"Origin": "http://localhost:8000"}
    response = client.options("/users/", headers=headers)
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "*"