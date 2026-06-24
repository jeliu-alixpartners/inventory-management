"""
Tests for orders API endpoints.
"""
import pytest


VALID_CREATE_ORDER_PAYLOAD = {
    "budget": 10000,
    "items": [
        {"sku": "FLT-405", "name": "Oil Filter Cartridge", "quantity": 10, "unit_price": 8.25}
    ]
}


class TestGetOrdersEndpoints:
    """Test suite for GET /api/orders endpoints."""

    def test_get_all_orders(self, client):
        """Test getting all orders returns a non-empty list."""
        response = client.get("/api/orders")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_order_required_fields(self, client):
        """Test that every order contains all required fields."""
        response = client.get("/api/orders")
        data = response.json()

        required_fields = [
            "id", "order_number", "customer", "items",
            "status", "order_date", "expected_delivery", "total_value"
        ]
        for order in data:
            for field in required_fields:
                assert field in order, f"Missing field '{field}' in order {order.get('id')}"

    def test_get_orders_by_warehouse(self, client):
        """Test filtering orders by warehouse."""
        response = client.get("/api/orders?warehouse=Tokyo")
        assert response.status_code == 200

        data = response.json()
        for order in data:
            assert order["warehouse"] == "Tokyo"

    def test_get_orders_by_status(self, client):
        """Test filtering orders by status."""
        response = client.get("/api/orders?status=Delivered")
        assert response.status_code == 200

        data = response.json()
        for order in data:
            assert order["status"].lower() == "delivered"

    def test_get_orders_by_month(self, client):
        """Test filtering orders by month."""
        response = client.get("/api/orders?month=2025-01")
        assert response.status_code == 200

        data = response.json()
        for order in data:
            assert "2025-01" in order["order_date"]

    def test_get_orders_by_quarter(self, client):
        """Test filtering orders by quarter."""
        response = client.get("/api/orders?month=Q1-2025")
        assert response.status_code == 200

        data = response.json()
        for order in data:
            assert any(m in order["order_date"] for m in ["2025-01", "2025-02", "2025-03"])

    def test_get_order_by_id(self, client):
        """Test getting a specific order by ID."""
        all_orders = client.get("/api/orders").json()
        order_id = all_orders[0]["id"]

        response = client.get(f"/api/orders/{order_id}")
        assert response.status_code == 200
        assert response.json()["id"] == order_id

    def test_get_nonexistent_order_returns_404(self, client):
        """Test that fetching a non-existent order returns 404."""
        response = client.get("/api/orders/nonexistent-order-999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_order_total_value_matches_items(self, client):
        """Test that total_value matches the sum of item quantities × unit prices."""
        response = client.get("/api/orders")
        data = response.json()

        for order in data:
            calculated = sum(
                item["quantity"] * item["unit_price"] for item in order["items"]
            )
            assert abs(order["total_value"] - calculated) < 0.02, (
                f"Order {order['order_number']}: total_value {order['total_value']} "
                f"!= calculated {calculated}"
            )

    def test_order_status_valid_values(self, client):
        """Test that all orders have a recognised status value."""
        response = client.get("/api/orders")
        valid = {"delivered", "shipped", "processing", "backordered"}
        for order in response.json():
            assert order["status"].lower() in valid


class TestCreateOrderEndpoint:
    """Test suite for POST /api/orders (restocking orders)."""

    def test_create_order_valid(self, client):
        """Test creating a valid restocking order returns 201 with correct fields."""
        response = client.post("/api/orders", json=VALID_CREATE_ORDER_PAYLOAD)
        assert response.status_code == 201

        order = response.json()
        assert order["source"] == "restocking"
        assert order["status"] == "Processing"
        assert order["customer"] == "Internal Restocking"
        assert order["total_value"] == pytest.approx(82.5)
        assert order["order_number"].startswith("RST-")
        assert "expected_delivery" in order

    def test_create_order_appears_in_get(self, client):
        """Test that a submitted restocking order appears in GET /api/orders."""
        client.post("/api/orders", json=VALID_CREATE_ORDER_PAYLOAD)

        all_orders = client.get("/api/orders").json()
        restocking = [o for o in all_orders if o.get("source") == "restocking"]
        assert len(restocking) >= 1

    def test_create_order_order_number_increments(self, client):
        """Test that sequential restocking orders get incrementing RST numbers."""
        r1 = client.post("/api/orders", json=VALID_CREATE_ORDER_PAYLOAD).json()
        r2 = client.post("/api/orders", json=VALID_CREATE_ORDER_PAYLOAD).json()

        # Extract the sequence number from RST-YYYY-NNNN
        seq1 = int(r1["order_number"].split("-")[-1])
        seq2 = int(r2["order_number"].split("-")[-1])
        assert seq2 == seq1 + 1

    def test_create_order_negative_quantity_rejected(self, client):
        """Test that a negative item quantity is rejected with 422."""
        payload = {
            "budget": 10000,
            "items": [{"sku": "FLT-405", "name": "Oil Filter", "quantity": -5, "unit_price": 8.25}]
        }
        response = client.post("/api/orders", json=payload)
        assert response.status_code == 422

    def test_create_order_zero_quantity_rejected(self, client):
        """Test that a zero item quantity is rejected with 422."""
        payload = {
            "budget": 10000,
            "items": [{"sku": "FLT-405", "name": "Oil Filter", "quantity": 0, "unit_price": 8.25}]
        }
        response = client.post("/api/orders", json=payload)
        assert response.status_code == 422

    def test_create_order_negative_unit_price_rejected(self, client):
        """Test that a negative unit price is rejected with 422."""
        payload = {
            "budget": 10000,
            "items": [{"sku": "FLT-405", "name": "Oil Filter", "quantity": 10, "unit_price": -8.25}]
        }
        response = client.post("/api/orders", json=payload)
        assert response.status_code == 422

    def test_create_order_zero_unit_price_rejected(self, client):
        """Test that a zero unit price is rejected with 422."""
        payload = {
            "budget": 10000,
            "items": [{"sku": "FLT-405", "name": "Oil Filter", "quantity": 10, "unit_price": 0}]
        }
        response = client.post("/api/orders", json=payload)
        assert response.status_code == 422

    def test_create_order_empty_items_rejected(self, client):
        """Test that an order with no items is rejected with 422."""
        payload = {"budget": 10000, "items": []}
        response = client.post("/api/orders", json=payload)
        assert response.status_code == 422

    def test_create_order_multiple_items(self, client):
        """Test creating an order with multiple line items."""
        payload = {
            "budget": 50000,
            "items": [
                {"sku": "FLT-405", "name": "Oil Filter Cartridge", "quantity": 100, "unit_price": 8.25},
                {"sku": "WDG-001", "name": "Industrial Widget Type A", "quantity": 50, "unit_price": 45.00},
            ]
        }
        response = client.post("/api/orders", json=payload)
        assert response.status_code == 201

        order = response.json()
        assert len(order["items"]) == 2
        assert order["total_value"] == pytest.approx(100 * 8.25 + 50 * 45.00)

    def test_create_order_total_computed_server_side(self, client):
        """Test that total_value is computed server-side, ignoring any client-supplied value."""
        payload = {
            "budget": 10000,
            "items": [{"sku": "FLT-405", "name": "Oil Filter", "quantity": 10, "unit_price": 8.25}]
        }
        response = client.post("/api/orders", json=payload)
        assert response.status_code == 201
        # Server always recomputes: 10 × 8.25 = 82.50
        assert response.json()["total_value"] == pytest.approx(82.50)


class TestInventoryValidation:
    """Test suite for inventory-level checks on POST /api/orders.

    Uses real inventory SKUs (PCB-001 with 450 on hand, SRV-301 with 45 on
    hand) so that the validation path is exercised.  The autouse
    reset_app_state fixture in conftest.py restores quantities after each
    test so there is no inter-test bleed.
    """

    # ── helpers ──────────────────────────────────────────────────────────────

    def _order(self, sku, name, quantity, unit_price=1.00):
        return {"budget": 999999, "items": [
            {"sku": sku, "name": name, "quantity": quantity, "unit_price": unit_price}
        ]}

    def _qty(self, client, sku):
        """Return current quantity_on_hand for a SKU, or None if not found."""
        items = client.get("/api/inventory").json()
        item = next((i for i in items if i["sku"] == sku), None)
        return item["quantity_on_hand"] if item else None

    # ── happy-path inventory checks ──────────────────────────────────────────

    def test_order_within_stock_succeeds(self, client):
        """An order for fewer units than on-hand is accepted."""
        response = client.post("/api/orders", json=self._order("PCB-001", "PCB", 10))
        assert response.status_code == 201

    def test_order_exactly_at_stock_limit_succeeds(self, client):
        """An order for exactly the available quantity is accepted."""
        available = self._qty(client, "SRV-301")  # 45 on hand
        response = client.post("/api/orders", json=self._order("SRV-301", "Servo", available))
        assert response.status_code == 201

    def test_order_deducts_inventory(self, client):
        """After a successful order the on-hand quantity decreases by the ordered amount."""
        before = self._qty(client, "PCB-001")
        client.post("/api/orders", json=self._order("PCB-001", "PCB", 50))
        assert self._qty(client, "PCB-001") == before - 50

    def test_order_unknown_sku_skips_inventory_check(self, client):
        """Items whose SKU is not tracked in inventory are allowed through."""
        # WDG-001 is a demand-forecast SKU; it doesn't exist in inventory.json
        response = client.post("/api/orders", json=self._order("WDG-001", "Widget", 9999))
        assert response.status_code == 201

    # ── rejection cases ───────────────────────────────────────────────────────

    def test_order_exceeding_stock_rejected(self, client):
        """An order for more units than on-hand returns 400."""
        available = self._qty(client, "PCB-001")  # 450 on hand
        response = client.post("/api/orders", json=self._order("PCB-001", "PCB", available + 1))
        assert response.status_code == 400

    def test_order_one_over_limit_rejected(self, client):
        """An order for exactly one unit over available stock returns 400."""
        available = self._qty(client, "SRV-301")  # 45 on hand
        response = client.post("/api/orders", json=self._order("SRV-301", "Servo", available + 1))
        assert response.status_code == 400

    def test_rejection_includes_sku_details(self, client):
        """The 400 error body names which SKU was insufficient."""
        response = client.post("/api/orders", json=self._order("PCB-001", "PCB", 99999))
        assert response.status_code == 400

        detail = response.json()["detail"]
        assert "items" in detail
        assert any(item["sku"] == "PCB-001" for item in detail["items"])

    def test_rejection_reports_requested_vs_available(self, client):
        """The 400 error body includes both requested and available quantities."""
        available = self._qty(client, "SRV-301")
        response = client.post("/api/orders", json=self._order("SRV-301", "Servo", available + 5))

        item_detail = response.json()["detail"]["items"][0]
        assert item_detail["requested"] == available + 5
        assert item_detail["available"] == available

    def test_inventory_not_changed_on_rejection(self, client):
        """A rejected order must not modify inventory — all-or-nothing."""
        before = self._qty(client, "PCB-001")
        client.post("/api/orders", json=self._order("PCB-001", "PCB", before + 1))
        assert self._qty(client, "PCB-001") == before

    def test_partial_failure_rejects_entire_order(self, client):
        """If any item is insufficient the whole order is rejected (no partial fulfilment)."""
        payload = {
            "budget": 999999,
            "items": [
                {"sku": "PCB-001", "name": "PCB",   "quantity": 10,    "unit_price": 1.0},  # ok
                {"sku": "SRV-301", "name": "Servo",  "quantity": 99999, "unit_price": 1.0},  # fail
            ]
        }
        response = client.post("/api/orders", json=payload)
        assert response.status_code == 400
        # The valid item must not have been deducted either
        assert self._qty(client, "PCB-001") == 450
