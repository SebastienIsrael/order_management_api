def test_get_inventory_creates_zero_row(client, product):
    response = client.get(f"/api/v1/inventory/{product['id']}")

    assert response.status_code == 200
    assert response.json() == {
        "product_id": product["id"],
        "quantity_on_hand": 0,
    }


def test_add_in_movement(client, product):
    response = client.post(
        f"/api/v1/inventory/{product['id']}/movements",
        json={"quantity": 5, "movement_type": "in", "reason": "purchase"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["quantity_on_hand"] == 5


def test_add_out_movement(client, stocked_product):
    response = client.post(
        f"/api/v1/inventory/{stocked_product['id']}/movements",
        json={"quantity": 4, "movement_type": "out", "reason": "manual sale"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["quantity_on_hand"] == 6


def test_out_movement_without_stock_returns_409(client, product):
    response = client.post(
        f"/api/v1/inventory/{product['id']}/movements",
        json={"quantity": 1, "movement_type": "out", "reason": "manual sale"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Insufficient stock"


def test_adjustment_adds_quantity(client, product):
    response = client.post(
        f"/api/v1/inventory/{product['id']}/movements",
        json={"quantity": 3, "movement_type": "adjustment", "reason": "count"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["quantity_on_hand"] == 3


def test_movements_history(client, stocked_product):
    response = client.get(f"/api/v1/inventory/{stocked_product['id']}/movements")

    assert response.status_code == 200, response.text
    movements = response.json()
    assert len(movements) == 1
    assert movements[0]["movement_type"] == "in"
    assert movements[0]["quantity_delta"] == 10
    assert movements[0]["reason"] == "test setup"


def test_inventory_for_missing_product_returns_404(client):
    response = client.get("/api/v1/inventory/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"
