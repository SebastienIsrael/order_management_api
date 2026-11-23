from decimal import Decimal


def _order_payload(product_id: int, quantity: int = 1, reference: str = "C1"):
    return {
        "customer_reference": reference,
        "items": [{"product_id": product_id, "quantity": quantity}],
    }


def test_create_order_consolidates_duplicate_items_and_decrements_stock(
    client, stocked_product
):
    response = client.post(
        "/api/v1/orders",
        json={
            "customer_reference": "C1",
            "items": [
                {"product_id": stocked_product["id"], "quantity": 2},
                {"product_id": stocked_product["id"], "quantity": 3},
            ],
        },
    )

    assert response.status_code == 201, response.text
    order = response.json()
    assert len(order["items"]) == 1
    assert order["items"][0]["quantity"] == 5
    assert Decimal(order["total_amount"]) == Decimal("500.00")
    assert order["status"] == "CONFIRMED"

    inventory = client.get(f"/api/v1/inventory/{stocked_product['id']}")
    assert inventory.json()["quantity_on_hand"] == 5

    movements = client.get(f"/api/v1/inventory/{stocked_product['id']}/movements")
    assert movements.json()[-1]["reason"] == "order_created"
    assert movements.json()[-1]["quantity_delta"] == -5


def test_order_with_insufficient_stock_does_not_create_order(client, stocked_product):
    response = client.post(
        "/api/v1/orders", json=_order_payload(stocked_product["id"], quantity=11)
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Insufficient stock"

    orders = client.get("/api/v1/orders")
    assert orders.json() == []

    inventory = client.get(f"/api/v1/inventory/{stocked_product['id']}")
    assert inventory.json()["quantity_on_hand"] == 10


def test_order_with_inactive_product_returns_409(client, stocked_product):
    client.patch(f"/api/v1/products/{stocked_product['id']}/status")

    response = client.post(
        "/api/v1/orders", json=_order_payload(stocked_product["id"])
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Product inactive"


def test_order_with_missing_product_returns_404(client):
    response = client.post("/api/v1/orders", json=_order_payload(999))

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_idempotency_key_returns_the_same_order(client, stocked_product):
    payload = _order_payload(stocked_product["id"], quantity=2)
    headers = {"Idempotency-Key": "checkout-123"}

    first = client.post("/api/v1/orders", json=payload, headers=headers)
    second = client.post("/api/v1/orders", json=payload, headers=headers)

    assert first.status_code == 201, first.text
    assert second.status_code == 201, second.text
    assert first.json()["id"] == second.json()["id"]
    assert first.json()["order_number"] == second.json()["order_number"]

    inventory = client.get(f"/api/v1/inventory/{stocked_product['id']}")
    assert inventory.json()["quantity_on_hand"] == 8


def test_idempotency_key_with_different_payload_returns_409(client, stocked_product):
    headers = {"Idempotency-Key": "checkout-123"}

    first = client.post(
        "/api/v1/orders",
        json=_order_payload(stocked_product["id"], quantity=2),
        headers=headers,
    )
    second = client.post(
        "/api/v1/orders",
        json=_order_payload(stocked_product["id"], quantity=3),
        headers=headers,
    )

    assert first.status_code == 201, first.text
    assert second.status_code == 409
    assert second.json()["detail"] == (
        "Idempotency key reused with a different payload"
    )


def test_cancel_order_restores_stock_and_records_movement(client, stocked_product):
    created = client.post(
        "/api/v1/orders",
        json=_order_payload(stocked_product["id"], quantity=4),
    )
    order_id = created.json()["id"]

    response = client.post(f"/api/v1/orders/{order_id}/cancel")

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "CANCELLED"

    inventory = client.get(f"/api/v1/inventory/{stocked_product['id']}")
    assert inventory.json()["quantity_on_hand"] == 10

    movements = client.get(f"/api/v1/inventory/{stocked_product['id']}/movements")
    assert movements.json()[-1]["reason"] == "order_cancelled"
    assert movements.json()[-1]["quantity_delta"] == 4


def test_cancel_twice_returns_409(client, stocked_product):
    created = client.post(
        "/api/v1/orders",
        json=_order_payload(stocked_product["id"]),
    )
    order_id = created.json()["id"]

    first = client.post(f"/api/v1/orders/{order_id}/cancel")
    second = client.post(f"/api/v1/orders/{order_id}/cancel")

    assert first.status_code == 200
    assert second.status_code == 409
    assert second.json()["detail"] == "Order already cancelled"


def test_list_orders_filters_by_status(client, stocked_product):
    created = client.post(
        "/api/v1/orders",
        json=_order_payload(stocked_product["id"]),
    )
    client.post(f"/api/v1/orders/{created.json()['id']}/cancel")

    cancelled = client.get("/api/v1/orders?status=CANCELLED")
    confirmed = client.get("/api/v1/orders?status=CONFIRMED")

    assert cancelled.status_code == 200
    assert [order["status"] for order in cancelled.json()] == ["CANCELLED"]
    assert confirmed.status_code == 200
    assert confirmed.json() == []


def test_invalid_order_status_filter_returns_422(client):
    response = client.get("/api/v1/orders?status=INVALID")

    assert response.status_code == 422


def test_missing_order_returns_404(client):
    response = client.get("/api/v1/orders/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"
