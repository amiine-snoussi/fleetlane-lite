from fastapi.testclient import TestClient
from app.main import app

def test_checkout_checkin_and_sign_flow():
    with TestClient(app) as client:
        v = client.post("/api/vehicles", json={"plate": "ZZZ999", "mileage": 1000, "location": "MTL"})
        assert v.status_code == 201
        vehicle_id = v.json()["id"]

        c = client.post("/api/customers", json={"name": "Alice", "contact": "alice@example.com"})
        assert c.status_code == 201
        customer_id = c.json()["id"]

        r = client.post("/api/reservations", json={
            "customer_id": customer_id,
            "vehicle_id": vehicle_id,
            "start_at": "2026-03-04T10:00:00",
            "end_at": "2026-03-04T12:00:00"
        })
        assert r.status_code == 201
        reservation_id = r.json()["id"]

        # sign
        s = client.post(f"/api/reservations/{reservation_id}/sign", json={"signed_by": "Alice"})
        assert s.status_code == 200
        body = s.json()
        assert body["reservation_id"] == reservation_id
        assert body["signed_by"] == "Alice"
        assert body["signed_at"] is not None

        # checkout
        co = client.post(f"/api/reservations/{reservation_id}/checkout", json={"mileage_out": 1100})
        assert co.status_code == 200
        assert co.json()["status"] == "OUT"
        assert co.json()["mileage_out"] == 1100

        v_after_checkout = client.get(f"/api/vehicles/{vehicle_id}")
        assert v_after_checkout.status_code == 200
        assert v_after_checkout.json()["status"] == "OUT"
        assert v_after_checkout.json()["mileage"] == 1100

        # checkin
        ci = client.post(f"/api/reservations/{reservation_id}/checkin", json={"mileage_in": 1200, "notes": "OK"})
        assert ci.status_code == 200
        assert ci.json()["status"] == "COMPLETED"
        assert ci.json()["mileage_in"] == 1200
        assert ci.json()["checkin_notes"] == "OK"

        v_after_checkin = client.get(f"/api/vehicles/{vehicle_id}")
        assert v_after_checkin.status_code == 200
        assert v_after_checkin.json()["status"] == "AVAILABLE"
        assert v_after_checkin.json()["mileage"] == 1200
