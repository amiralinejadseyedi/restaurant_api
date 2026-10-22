
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.database import Base, get_db
from sqlalchemy.exc import SQLAlchemyError

TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "restaurant api is running"
    }


def test_create_order(client):
    response = client.post(
        "/orders",
        json={
            "customer_name": "Test Customer",
            "food_name": "Koobideh",
            "quantity": 2,
            "price": 1000,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["message"] == "Order created successfully"
    assert data["order"]["customer_name"] == "Test Customer"
    assert data["order"]["food_name"] == "Koobideh"
    assert data["order"]["quantity"] == 2
    assert data["order"]["price"] == 1000
    assert "id" in data["order"]



def test_create_order_with_invalid_quantity(client):
    response = client.post(
        "/orders",
        json={
            "customer_name": "Test Customer",
            "food_name": "Koobideh",
            "quantity": 0,
            "price": 1000,
        },
    )

    assert response.status_code == 422

def test_delete_nonexistent_order(client):
    response = client.delete("/orders/9999")

    assert response.status_code == 404
    assert response.json() == {
    "detail": "order not found"
    }



def test_get_orders(client):
    create_response = client.post(
        "/orders",
        json={
            "customer_name": "Amir",
            "food_name": "Koobideh",
            "quantity": 2,
            "price": 1000,
        },
    )
    assert create_response.status_code == 201

    response = client.get("/orders")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["customer_name"] == "Amir"


def test_update_order(client):
    create_response = client.post(
        "/orders",
        json={
            "customer_name": "Amir",
            "food_name": "Koobideh",
            "quantity": 2,
            "price": 1000,
        },
    )
    assert create_response.status_code == 201
    order_id = create_response.json()["order"]["id"]

    response = client.put(
        f"/orders/{order_id}",
        json={
            "customer_name": "Amir Updated",
            "food_name": "Joojeh",
            "quantity": 3,
            "price": 1500,
        },
    )

    assert response.status_code == 200
    assert response.json()["customer_name"] == "Amir Updated"
    assert response.json()["food_name"] == "Joojeh"
    assert response.json()["quantity"] == 3
    assert response.json()["price"] == 1500


def test_delete_order(client):
    create_response = client.post(
        "/orders",
        json={
            "customer_name": "Amir",
            "food_name": "Koobideh",
            "quantity": 2,
            "price": 1000,
        },
    )
    assert create_response.status_code == 201
    order_id = create_response.json()["order"]["id"]

    delete_response = client.delete(f"/orders/{order_id}")

    assert delete_response.status_code == 200

    get_response = client.get("/orders")
    assert get_response.status_code == 200
    assert get_response.json() == []

def test_create_order_with_invalid_price(client):
    response = client.post(
        "/orders",
        json={
            "customer_name": "Test Customer",
            "food_name": "Koobideh",
            "quantity": 2,
            "price": 0,
        },
    )

    assert response.status_code == 422


def test_update_nonexistent_order(client):
    response = client.put(
        "/orders/9999",
        json={
            "customer_name": "Test Customer",
            "food_name": "Koobideh",
            "quantity": 2,
            "price": 1000,
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Order not found"}


def test_create_order_with_spaces_only_name(client):
    response = client.post(
        "/orders",
        json={
            "customer_name": "   ",
            "food_name": "Koobideh",
            "quantity": 2,
            "price": 1000,
        },
    )

    assert response.status_code == 422


    from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import patch


def test_create_order_database_error(client):
    with patch(
        "app.main.Session.commit",
        side_effect=SQLAlchemyError("Database failure")
    ):
        response = client.post(
            "/orders",
            json={
                "customer_name": "Amir",
                "food_name": "Koobideh",
                "quantity": 2,
                "price": 1000,
            },
        )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Database error while creating order"
    }



def test_update_order_database_error(client):
    create_response = client.post(
        "/orders",
        json={
            "customer_name": "Amir",
            "food_name": "Koobideh",
            "quantity": 2,
            "price": 1000,
        },
    )
    assert create_response.status_code == 201

    order_id = create_response.json()["order"]["id"]

    with patch(
        "app.main.Session.commit",
        side_effect=SQLAlchemyError("Database failure")
    ):
        response = client.put(
            f"/orders/{order_id}",
            json={
                "customer_name": "Amir Updated",
                "food_name": "Joojeh",
                "quantity": 3,
                "price": 1500,
            },
        )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Database error while updating order"
    }



def test_delete_order_database_error(client):
    create_response = client.post(
        "/orders",
        json={
            "customer_name": "Amir",
            "food_name": "Koobideh",
            "quantity": 2,
            "price": 1000,
        },
    )
    assert create_response.status_code == 201

    order_id = create_response.json()["order"]["id"]

    with patch(
        "app.main.Session.commit",
        side_effect=SQLAlchemyError("Database failure")
    ):
        response = client.delete(f"/orders/{order_id}")

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Database error while deleting order"
    }

def test_get_orders_database_error(client):
    with patch(
        "app.main.Session.execute",
        side_effect=SQLAlchemyError("Database failure")
    ):
        response = client.get("/orders")

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Database error while retrieving orders"
    }
