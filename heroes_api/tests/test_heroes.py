# CREATE HERO TESTS
def test_create_hero(client, auth_headers):
    response = client.post("/heroes/", json={"name": "John Doe", "power": "Programming"}, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["power"] == "Programming"
    assert data["level"] == 1
    assert data["active"] is True

def test_create_hero_unauthenticated(client):
    response = client.post("/heroes/", json={"name": "John Doe", "power": "Programming"})
    assert response.status_code == 401

def test_create_hero_short_name(client, auth_headers):
    response = client.post("/heroes/", json={"name": "AB", "power": "Programming"}, headers=auth_headers)
    assert response.status_code == 422


# GET ALL HEROES TESTS
def test_get_heroes_empty(client):
    response = client.get("/heroes/")
    assert response.status_code == 200
    assert response.json() == []

def test_get_heroes(client, auth_headers):
    client.post("/heroes/", json={"name": "John Doe", "power": "Programming"}, headers=auth_headers)
    client.post("/heroes/", json={"name": "Alice Doe", "power": "Debugging"}, headers=auth_headers)
    response = client.get("/heroes/")
    assert response.status_code == 200
    assert len(response.json()) == 2


# GET HERO BY ID TESTS
def test_get_hero_by_id(client, auth_headers):
    created = client.post("/heroes/", json={"name": "John Doe", "power": "Programming"}, headers=auth_headers).json()
    response = client.get(f"/heroes/{created['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "John Doe"

def test_get_hero_not_found(client):
    response = client.get("/heroes/999")
    assert response.status_code == 404


# UPDATE HERO TESTS
def test_update_hero(client, auth_headers):
    created = client.post("/heroes/", json={"name": "John Doe", "power": "Programming"}, headers=auth_headers).json()
    response = client.patch(f"/heroes/{created['id']}", json={"name": "Alice Doe"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Alice Doe"
    assert response.json()["power"] == "Programming"  # unchanged

def test_update_hero_unauthenticated(client, auth_headers):
    created = client.post("/heroes/", json={"name": "John Doe", "power": "Programming"}, headers=auth_headers).json()
    response = client.patch(f"/heroes/{created['id']}", json={"name": "Alice Doe"})
    assert response.status_code == 401

def test_update_hero_not_found(client, auth_headers):
    response = client.patch("/heroes/100", json={"name": "Glitch"}, headers=auth_headers)
    assert response.status_code == 404


# DELETE HERO TESTS
def test_delete_hero(client, admin_headers):
    created = client.post("/heroes/", json={"name": "John Doe", "power": "Programming"}, headers=admin_headers).json()
    response = client.delete(f"/heroes/{created['id']}", headers=admin_headers)
    assert response.status_code == 204

def test_delete_hero_non_admin(client, auth_headers, admin_headers):
    created = client.post("/heroes/", json={"name": "John Doe", "power": "Programming"}, headers=admin_headers).json()
    response = client.delete(f"/heroes/{created['id']}", headers=auth_headers)
    assert response.status_code == 403

def test_delete_hero_with_active_mission(client, admin_headers):
    hero = client.post("/heroes/", json={"name": "John Doe", "power": "Programming"}, headers=admin_headers).json()
    client.post("/missions/", json={"title": "Save the city", "difficulty": 5, "hero_id": hero["id"]}, headers=admin_headers)
    response = client.delete(f"/heroes/{hero['id']}", headers=admin_headers)
    assert response.status_code == 400

def test_delete_hero_not_found(client, admin_headers):
    response = client.delete("/heroes/100", headers=admin_headers)
    assert response.status_code == 404