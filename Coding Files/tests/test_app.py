from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db

init_db()

client = TestClient(app)


def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "FitBuddy" in response.text


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_users_api_empty_or_valid():
    response = client.get("/api/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
