from pathlib import Path

import pytest

from app import app as flask_app


@pytest.fixture()
def client(tmp_path):
    database = tmp_path / "test_sakhimart.db"
    flask_app.config.update(
        TESTING=True,
        SECRET_KEY="test-only-secret",
        DATABASE=str(database),
    )
    with flask_app.test_client() as test_client:
        yield test_client


def register_and_login(client):
    response = client.post("/register", data={
        "name": "Test Member",
        "username": "testmember",
        "password": "SakhiMart@2026",
    }, follow_redirects=True)
    assert response.status_code == 200
    response = client.post("/login", data={
        "username": "testmember",
        "password": "SakhiMart@2026",
    }, follow_redirects=True)
    assert response.status_code == 200


def test_database_initializes_and_health_works(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "database": "connected"}


def test_registration_login_and_logout(client):
    register_and_login(client)
    response = client.get("/")
    assert response.status_code == 200
    response = client.post("/logout", follow_redirects=True)
    assert response.status_code == 200


def test_product_and_savings_workflow(client):
    register_and_login(client)

    response = client.post("/products/add", data={
        "name": "Handmade Bag",
        "description": "Jute bag",
        "price": "250.00",
        "stock": "4",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Handmade Bag" in response.data

    response = client.post("/savings/add", data={
        "kind": "deposit", "amount": "500", "note": "Weekly savings",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"500.00" in response.data

    response = client.post("/savings/add", data={
        "kind": "withdrawal", "amount": "100", "note": "Test withdrawal",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"400.00" in response.data


def test_withdrawal_cannot_exceed_balance(client):
    register_and_login(client)
    response = client.post("/savings/add", data={
        "kind": "withdrawal", "amount": "50", "note": "Too much",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Insufficient balance" in response.data


def test_business_advisor_route_is_available(client):
    response = client.get("/advisor/")
    assert response.status_code == 200
    assert b"SakhiMart Business Advisor" in response.data
