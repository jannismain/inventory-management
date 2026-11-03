"""
Tests for purchase order endpoints and has_purchase_order on /api/backlog.
"""
import pytest

from main import purchase_orders


@pytest.fixture(autouse=True)
def clean_purchase_orders():
    """Purchase orders live in module-level state; isolate each test."""
    purchase_orders.clear()
    yield
    purchase_orders.clear()


def payload(**overrides):
    body = {
        "backlog_item_id": "1",
        "supplier_name": "Acme Supply",
        "quantity": 350,
        "unit_cost": 12.5,
        "expected_delivery_date": "2025-12-01",
        "notes": "Rush",
    }
    body.update(overrides)
    return body


class TestCreatePurchaseOrder:
    def test_create_success(self, client):
        response = client.post("/api/purchase-orders", json=payload())
        assert response.status_code == 201
        data = response.json()
        assert data["id"].startswith("PO-")
        assert data["backlog_item_id"] == "1"
        assert data["status"] == "Pending"
        assert data["quantity"] == 350

    def test_backlog_reflects_purchase_order(self, client):
        before = {i["id"]: i["has_purchase_order"] for i in client.get("/api/backlog").json()}
        assert not any(before.values())
        client.post("/api/purchase-orders", json=payload())
        after = {i["id"]: i["has_purchase_order"] for i in client.get("/api/backlog").json()}
        assert after["1"] is True
        assert after["2"] is False

    def test_duplicate_returns_409(self, client):
        client.post("/api/purchase-orders", json=payload())
        assert client.post("/api/purchase-orders", json=payload()).status_code == 409

    def test_unknown_backlog_item_returns_404(self, client):
        assert client.post("/api/purchase-orders", json=payload(backlog_item_id="999")).status_code == 404

    @pytest.mark.parametrize("override", [
        {"quantity": 0},
        {"quantity": -5},
        {"unit_cost": -1},
        {"supplier_name": "   "},
        {"expected_delivery_date": "not-a-date"},
    ])
    def test_invalid_input_returns_400(self, client, override):
        assert client.post("/api/purchase-orders", json=payload(**override)).status_code == 400

    def test_missing_field_returns_422(self, client):
        body = payload()
        del body["supplier_name"]
        assert client.post("/api/purchase-orders", json=body).status_code == 422


class TestGetPurchaseOrder:
    def test_get_existing(self, client):
        created = client.post("/api/purchase-orders", json=payload()).json()
        response = client.get("/api/purchase-orders/1")
        assert response.status_code == 200
        assert response.json() == created

    def test_get_missing_returns_404(self, client):
        assert client.get("/api/purchase-orders/1").status_code == 404
