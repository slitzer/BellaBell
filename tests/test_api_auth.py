from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import PriceObservation, Item, User


client = TestClient(app)


def _clear_data() -> None:
    with SessionLocal() as db:
        db.query(PriceObservation).delete()
        db.query(Item).delete()
        db.query(User).delete()
        db.commit()


def setup_function():
    _clear_data()


def teardown_function():
    _clear_data()


def test_items_requires_user_header():
    response = client.get("/items")

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing X-User-Id header"


def test_items_are_isolated_per_user():
    payload = {
        "name": "Monitor Laptop",
        "url": "https://example.com/laptop",
        "css_selector": ".price",
        "check_interval_minutes": 60,
    }

    create_response = client.post("/items", json=payload, headers={"X-User-Id": "alice"})
    assert create_response.status_code == 200

    alice_items = client.get("/items", headers={"X-User-Id": "alice"})
    bob_items = client.get("/items", headers={"X-User-Id": "bob"})

    assert alice_items.status_code == 200
    assert len(alice_items.json()) == 1
    assert alice_items.json()[0]["owner_id"] is not None

    assert bob_items.status_code == 200
    assert bob_items.json() == []


def test_user_cannot_access_another_users_history():
    payload = {
        "name": "Monitor Phone",
        "url": "https://example.com/phone",
        "css_selector": ".price",
        "check_interval_minutes": 60,
    }

    created_item = client.post("/items", json=payload, headers={"X-User-Id": "alice"}).json()

    forbidden_response = client.get(
        f"/items/{created_item['id']}/history", headers={"X-User-Id": "bob"}
    )

    assert forbidden_response.status_code == 404
    assert forbidden_response.json()["detail"] == "Item not found"
