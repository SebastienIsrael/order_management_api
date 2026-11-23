from decimal import Decimal


def test_create_product_persists_decimal_price(client):
    response = client.post(
        "/api/v1/products",
        json={
            "sku": "GPU-0001",
            "name": "Placa de video",
            "description": "32GB",
            "unit_price": "12999.90",
        },
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert Decimal(body["unit_price"]) == Decimal("12999.90")
    assert body["is_active"] is True

    persisted = client.get(f"/api/v1/products/{body['id']}")
    assert persisted.status_code == 200
    assert Decimal(persisted.json()["unit_price"]) == Decimal("12999.90")


def test_duplicate_sku_returns_409(client, product):
    response = client.post(
        "/api/v1/products",
        json={
            "sku": product["sku"],
            "name": "Outro produto",
            "unit_price": "50.00",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "SKU already exists"


def test_update_product_returns_updated_values(client, product):
    response = client.patch(
        f"/api/v1/products/{product['id']}",
        json={"name": "Teclado atualizado", "unit_price": "150.00"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["name"] == "Teclado atualizado"
    assert Decimal(body["unit_price"]) == Decimal("150.00")
    assert body["updated_at"] is not None


def test_empty_update_returns_current_product(client, product):
    response = client.patch(f"/api/v1/products/{product['id']}", json={})

    assert response.status_code == 200, response.text
    assert response.json()["id"] == product["id"]
    assert response.json()["name"] == product["name"]


def test_invalid_price_returns_422(client):
    response = client.post(
        "/api/v1/products",
        json={"sku": "BAD-001", "name": "Invalido", "unit_price": "0"},
    )

    assert response.status_code == 422


def test_missing_product_returns_404(client):
    response = client.get("/api/v1/products/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_toggle_product_status(client, product):
    response = client.patch(f"/api/v1/products/{product['id']}/status")

    assert response.status_code == 200, response.text
    assert response.json()["is_active"] is False
