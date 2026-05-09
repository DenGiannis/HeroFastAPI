import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import get_session

# In-memory SQLite created for each test session
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

# Override the app's DB session with the test session
@pytest.fixture(name="client")
def client_fixture(session: Session):
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client):
    """Headers for a regular authenticated user."""
    client.post("/auth/register", json={"username": "regularuser", "password": "password123"})
    token = client.post("/auth/login", data={"username": "regularuser", "password": "password123"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(name="admin_headers")
def admin_headers_fixture(client, session):
    """Headers for an admin user."""
    client.post("/auth/register", json={"username": "adminuser", "password": "adminpass", "is_admin": True})
    token = client.post("/auth/login", data={"username": "adminuser", "password": "adminpass"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}