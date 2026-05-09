# Helper
def create_hero(client, headers, name="John Doe", power="Programming"):
    return client.post("/heroes/", json={"name": name, "power": power}, headers=headers).json()

def create_mission(client, headers, title="Solve the production bug", difficulty=5, hero_id=1):
    return client.post("/missions/", json={"title": title, "difficulty": difficulty, "hero_id": hero_id}, headers=headers)

# CREATE MISSION TESTS
def test_create_mission(client, auth_headers):
    hero = create_hero(client, auth_headers)
    response = create_mission(client, auth_headers, hero_id=hero["id"])
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Solve the production bug"
    assert data["difficulty"] == 5
    assert data["completed"] is False
    assert data["hero_id"] == hero["id"]

def test_create_mission_unauthenticated(client, auth_headers):
    hero = create_hero(client, auth_headers)
    response = client.post(
        "/missions/",
        json={"title": "Solve the production bug", "difficulty": 5, "hero_id": hero["id"]}
    )
    assert response.status_code == 401

def test_create_mission_hero_not_found(client, auth_headers):
    response = create_mission(client, auth_headers, hero_id=100)
    assert response.status_code == 404

def test_create_mission_invalid_difficulty(client, auth_headers):
    hero = create_hero(client, auth_headers)
    response = create_mission(client, auth_headers, difficulty=100, hero_id=hero["id"])
    assert response.status_code == 422


# GET ALL MISSIONS TESTS
def test_get_missions_empty(client):
    response = client.get("/missions/")
    assert response.status_code == 200
    assert response.json() == []

def test_get_missions(client, auth_headers):
    hero = create_hero(client, auth_headers)
    create_mission(client, auth_headers, title="Easy Mission", difficulty=1, hero_id=hero["id"])
    create_mission(client, auth_headers, title="Difficult Mission", difficulty=8, hero_id=hero["id"])
    response = client.get("/missions/")
    assert response.status_code == 200
    assert len(response.json()) == 2


# GET MISSION BY ID TESTS
def test_get_mission_by_id(client, auth_headers):
    hero = create_hero(client, auth_headers)
    created = create_mission(client, auth_headers, hero_id=hero["id"]).json()
    response = client.get(f"/missions/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Solve the production bug"
    assert response.json()["difficulty"] == 5
    assert response.json()["completed"] is False
    assert response.json()["hero_id"] == hero["id"]

def test_get_mission_not_found(client):
    response = client.get("/missions/999")
    assert response.status_code == 404


# UPDATE MISSION TESTS
def test_update_mission(client, auth_headers):
    hero = create_hero(client, auth_headers)
    created = create_mission(client, auth_headers, hero_id=hero["id"]).json()
    response = client.patch(f"/missions/{created['id']}", json={"completed": True, "title": "Become an AI Engineer"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["completed"] is True
    assert response.json()["title"] == "Become an AI Engineer"
    assert response.json()["difficulty"] == 5  # unchanged
    assert response.json()["hero_id"] == hero["id"]  # unchanged

def test_update_mission_reassign_hero(client, auth_headers):
    hero1 = create_hero(client, auth_headers, name="John Doe", power="Programming")
    hero2 = create_hero(client, auth_headers, name="Alice Doe", power="Debugging")
    created = create_mission(client, auth_headers, hero_id=hero1["id"]).json()
    response = client.patch(f"/missions/{created['id']}", json={"hero_id": hero2["id"]}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["hero_id"] == hero2["id"]

def test_update_mission_reassign_invalid_hero(client, auth_headers):
    hero = create_hero(client, auth_headers)
    created = create_mission(client, auth_headers, hero_id=hero["id"]).json()
    response = client.patch(f"/missions/{created['id']}", json={"hero_id": 999}, headers=auth_headers)
    assert response.status_code == 404

def test_update_mission_not_found(client, auth_headers):
    response = client.patch("/missions/999", json={"completed": True}, headers=auth_headers)
    assert response.status_code == 404


# -DELETE MISSION TESTS
def test_delete_mission(client, admin_headers):
    hero = create_hero(client, admin_headers)
    created = create_mission(client, admin_headers, hero_id=hero["id"]).json()
    response = client.delete(f"/missions/{created['id']}", headers=admin_headers)
    assert response.status_code == 204

def test_delete_mission_non_admin(client, auth_headers, admin_headers):
    hero = create_hero(client, admin_headers)
    created = create_mission(client, admin_headers, hero_id=hero["id"]).json()
    response = client.delete(f"/missions/{created['id']}", headers=auth_headers)
    assert response.status_code == 403

def test_delete_mission_not_found(client, admin_headers):
    response = client.delete("/missions/999", headers=admin_headers)
    assert response.status_code == 404
