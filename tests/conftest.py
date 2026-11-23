import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  (register all ORM models)
from app.db.base import Base
from app.db.session import get_db
from app.main import app


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def product(client):
    response = client.post(
        "/api/v1/products",
        json={
            "sku": "PROD-001",
            "name": "Teclado mecanico",
            "description": "Switch azul",
            "unit_price": "100.00",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture()
def stocked_product(client, product):
    response = client.post(
        f"/api/v1/inventory/{product['id']}/movements",
        json={
            "quantity": 10,
            "movement_type": "in",
            "reason": "test setup",
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["quantity_on_hand"] == 10
    return product
