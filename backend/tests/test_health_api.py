from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoints():
    with TestClient(app) as client:
        root_health = client.get("/health")
        assert root_health.status_code == 200
        assert root_health.json() == {"status": "ok"}

        api_health = client.get("/api/health")
        assert api_health.status_code == 200
        assert api_health.json() == {"status": "ok"}
