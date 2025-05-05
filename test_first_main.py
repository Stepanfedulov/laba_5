from fastapi.testclient import TestClient


from main import app
client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200


def test_get_users():
    headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjMiLCJleHAiOjE3Mzk5NTQ2NzZ9.tMKZJzUX_heuhdbVHxWW4-OdiTCXa9AvKbSXkAwmrmw"} 
    response = client.get("/users/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["username"] == "123"

def test_create_user():
    response = client.post(
    "/register/",
    json={"username": "testuser4", "email": "testuser4@example.com",
    "full_name": "Test User", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser4"
    assert data["email"] == "testuser4@example.com"