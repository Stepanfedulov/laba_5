#TESTS FastAPI
from fastapi.testclient import TestClient


from main import app
client = TestClient(app)


def test_create_user():
    response = client.post(
        "/register/",
        json={"username": "testuser5", "email": "testuser5@example.com",
              "full_name": "Test User", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser5"
    assert data["email"] == "testuser5@example.com"

# Тест на повторную регистрацию с тем же username/email
def test_duplicate_registration():
    response = client.post(
        "/register/",
        json={"username": "testuser5", "email": "testuser@example.com",
              "full_name": "Test User", "password": "password123"},
    )
    assert response.status_code == 200

# Тест аутентификации
def test_login():
    response = client.post(
        "/token",
        data={"username": "testuser5", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

# Тест аутентификации с неверным паролем
def test_login_invalid_password():
    response = client.post(
        "/token",
        data={"username": "testuser5", "password": "wrongpassword"},
    )
    assert response.status_code == 401 

# Тест получения списка пользователей
def test_get_users():
    headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjMiLCJleHAiOjE3Mzk5NTQ2NzZ9.tMKZJzUX_heuhdbVHxWW4-OdiTCXa9AvKbSXkAwmrmw"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

# Тест получения информации о текущем пользователе
def test_get_current_user():
    headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjMiLCJleHAiOjE3Mzk5NTQ2NzZ9.tMKZJzUX_heuhdbVHxWW4-OdiTCXa9AvKbSXkAwmrmw"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "username" in data

# Тест удаления пользователя
def test_delete_user():
    headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjMiLCJleHAiOjE3Mzk5NTQ2NzZ9.tMKZJzUX_heuhdbVHxWW4-OdiTCXa9AvKbSXkAwmrmw"}
    response = client.delete("/users/402", headers=headers)
    assert response.status_code == 200
    response = client.delete("/users/402", headers=headers)
    assert response.status_code == 404

# Тест обновления пользователя
def test_update_user():
    headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjMiLCJleHAiOjE3Mzk5NTQ2NzZ9.tMKZJzUX_heuhdbVHxWW4-OdiTCXa9AvKbSXkAwmrmw"}
    response = client.put(
        "/users/3",
        headers=headers,
        json={"full_name": "newemail@example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "newemail@example.com"



# Тестирование CORS
def test_cors_allowed():
    headers = {"Origin": "http://127.0.0.1:8000"}
    response = client.options("/users/")
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "*"

def test_cors_blocked():
    headers = {"Origin": "http://unauthorized.com"}
    response = client.options("/users/")
    assert response.status_code == 200

# Тестирование обработки ошибок
def test_missing_field():
    response = client.post(
        "/register/",
        json={"username": "testuser6"}
    )
    assert response.status_code == 422

# Тестирование безопасности
def test_protected_route_without_token():
    response = client.get("/users/")
    assert response.status_code == 401

def test_protected_route_fake_token():
    headers = {"Authorization": "Bearer fake_token"}
    response = client.get("/users/")
    assert response.status_code == 401 

import time

def test_performance():
    start_time = time.time()
    for _ in range(10):
        client.get("/")
    end_time = time.time()
    assert (end_time - start_time) < 1