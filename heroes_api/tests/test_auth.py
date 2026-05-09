# REGISTER USER TESTS
def test_register(client):
    response = client.post("/auth/register", json={"username": "test-user", "password": "123456"})
    assert response.status_code == 201

def test_register_duplicate(client):
    client.post("/auth/register", json={"username": "test-user", "password": "123456"})
    response = client.post("/auth/register", json={"username": "test-user", "password": "123456"})
    assert response.status_code == 400

def test_register_short_username(client):
    response = client.post("/auth/register", json={"username": "ab", "password": "123456"})
    assert response.status_code == 422

def test_register_short_password(client):
    response = client.post("/auth/register", json={"username": "test-user", "password": "123"})
    assert response.status_code == 422


# LOGIN TESTS
def test_login(client):
    client.post("/auth/register", json={"username": "test-user", "password": "123456"})
    response = client.post("/auth/login", data={"username": "test-user", "password": "123456"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password(client):
    client.post("/auth/register", json={"username": "test-user", "password": "123456"})
    response = client.post("/auth/login", data={"username": "test-user", "password": "wrongpass"})
    assert response.status_code == 401

def test_login_nonexistent_user(client):
    response = client.post("/auth/login", data={"username": "ghost", "password": "123456"})
    assert response.status_code == 401


# GET CURRENT USER TESTS
def test_me(client):
    client.post("/auth/register", json={"username": "test-user", "password": "123456"})
    token = client.post("/auth/login", data={"username": "test-user", "password": "123456"}).json()["access_token"]
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "test-user"

def test_me_admin(client):
    client.post("/auth/register", json={"username": "admin-user", "password": "123456", "is_admin": True})
    token = client.post("/auth/login", data={"username": "admin-user", "password": "123456"}).json()["access_token"]
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "admin-user"
    assert response.json()["is_admin"] is True

def test_me_no_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401

def test_me_invalid_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401