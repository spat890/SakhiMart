import os
import tempfile

import pytest

from backend.app import create_app

PHONE = "9111111111"
PASSWORD = "secret123"


@pytest.fixture()
def client():
    handle, path = tempfile.mkstemp(suffix=".db")
    os.close(handle)
    app = create_app(path)
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with app.test_client() as test_client:
        yield test_client
    os.unlink(path)


def register(client, phone=PHONE, password=PASSWORD, name="Asha"):
    return client.post(
        "/register",
        data={"name": name, "phone": phone, "password": password},
        follow_redirects=True,
    )


def login(client, phone=PHONE, password=PASSWORD):
    return client.post(
        "/login",
        data={"phone": phone, "password": password},
        follow_redirects=True,
    )


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"SakhiMart" in response.data


def test_register_then_login(client):
    response = register(client)
    assert b"Account created" in response.data
    response = login(client)
    assert b"Welcome, Asha" in response.data


def test_duplicate_phone_rejected(client):
    register(client)
    response = register(client)
    assert response.status_code == 400
    assert b"already registered" in response.data


def test_wrong_password_rejected(client):
    register(client)
    response = login(client, password="nope123")
    assert response.status_code == 401
    assert b"Invalid phone number or password" in response.data


def test_logout(client):
    register(client)
    login(client)
    response = client.post("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Demo login" in response.data


def test_product_add_and_view(client):
    register(client)
    login(client)
    response = client.post(
        "/products",
        data={"name": "Millet biscuits", "price": "120", "stock": "8"},
        follow_redirects=True,
    )
    assert b"Product saved" in response.data
    assert "Millet biscuits".encode() in response.data
    assert b"Rs 120.00" in response.data


def test_product_rejects_negative_stock(client):
    register(client)
    login(client)
    response = client.post(
        "/products",
        data={"name": "Bad item", "price": "50", "stock": "-2"},
        follow_redirects=True,
    )
    assert b"Stock cannot be negative" in response.data


def test_product_requires_login(client):
    response = client.post(
        "/products",
        data={"name": "Anon", "price": "10", "stock": "1"},
        follow_redirects=True,
    )
    assert b"Login required" in response.data


def test_deposit_and_withdraw(client):
    register(client)
    login(client)
    client.post("/transactions", data={"kind": "deposit", "amount": "500", "note": "first"}, follow_redirects=True)
    response = client.post(
        "/transactions",
        data={"kind": "withdraw", "amount": "200", "note": "food"},
        follow_redirects=True,
    )
    assert b"Withdraw recorded" in response.data
    assert b"Rs 300.00" in response.data


def test_withdrawal_above_balance_rejected(client):
    register(client)
    login(client)
    client.post("/transactions", data={"kind": "deposit", "amount": "100", "note": ""}, follow_redirects=True)
    response = client.post(
        "/transactions",
        data={"kind": "withdraw", "amount": "150", "note": ""},
        follow_redirects=True,
    )
    assert b"Withdrawal exceeds available balance" in response.data
    assert b"Rs 100.00" in response.data


def test_zero_amount_rejected(client):
    register(client)
    login(client)
    response = client.post(
        "/transactions",
        data={"kind": "deposit", "amount": "0", "note": ""},
        follow_redirects=True,
    )
    assert b"Amount must be greater than zero" in response.data
