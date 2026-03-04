from fastapi.testclient import TestClient
from app.main import app

def test_reservation_overlap_returns_409():
    with TestClient(app) as client:
        v = client.post("/api/vehicles", json={"plate": "ABC123", "mileage": 100, "location": "MTL"})
        assert v.status_code == 201
        vehicle_id = v.json()["id"]

        c = client.post("/api/customers", json={"name": "John Doe", "contact": "john@example.com"})
        assert c.status_code == 201
        customer_id = c.json()["id"]

        r1 = client.post("/api/reservations", json={
            "customer_id": customer_id,
            "vehicle_id": vehicle_id,
            "start_at": "2026-03-04T10:00:00",
            "end_at": "2026-03-04T12:00:00"
        })
        assert r1.status_code == 201

        r2 = client.post("/api/reservations", json={
            "customer_id": customer_id,
            "vehicle_id": vehicle_id,
            "start_at": "2026-03-04T11:00:00",
            "end_at": "2026-03-04T13:00:00"
        })
        assert r2.status_code == 409
        assert "reserved" in r2.json()["detail"].lower()
