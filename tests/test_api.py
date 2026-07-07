import sys
sys.path.append(".")
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_districts():
    response = client.get("/districts")
    assert response.status_code == 200
    assert len(response.json()) > 0