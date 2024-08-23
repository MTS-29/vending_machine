import pytest
from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)


# Utility to reset data.json to its original state after each test
@pytest.fixture(autouse=True)
def reset_data():
    with open("data.json", "r") as file:
        original_data = json.load(file)
    yield
    with open("data.json", "w") as file:
        json.dump(original_data, file, indent=4)


def test_create_user():
    response = client.post("/users",
                           json={"username": "new_user", "password": "new_pass", "role": "buyer", "deposit": 0})
    assert response.status_code == 200
    assert response.json()["username"] == "new_user"


def test_create_user_existing():
    response = client.post("/users", json={"username": "seller1", "password": "pass1", "role": "seller", "deposit": 0})
    assert response.status_code == 400
    assert response.json() == {"detail": "User already exists"}


def test_get_products():
    response = client.get("/products")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_create_product_as_seller():
    # Login as seller
    seller = {"username": "seller1", "password": "pass1"}
    client.post("/switch_user", json=seller)

    product_data = {"productId": 3, "productName": "Candy", "amountAvailable": 50, "cost": 25, "sellerId": "seller1"}
    response = client.post("/products", json=product_data)
    assert response.status_code == 200
    assert response.json()["productName"] == "Candy"


def test_create_product_as_buyer():
    # Login as buyer
    buyer = {"username": "buyer1", "password": "pass2"}
    client.post("/switch_user", json=buyer)

    product_data = {"productId": 3, "productName": "Candy", "amountAvailable": 50, "cost": 25, "sellerId": "seller1"}
    response = client.post("/products", json=product_data)
    assert response.status_code == 403
    assert response.json() == {"detail": "Only sellers can add products"}


def test_update_product():
    # Login as seller
    seller = {"username": "seller1", "password": "pass1"}
    client.post("/switch_user", json=seller)

    updated_product_data = {"productId": 1, "productName": "Updated Soda", "amountAvailable": 30, "cost": 100,
                            "sellerId": "seller1"}
    response = client.put("/products/1", json=updated_product_data)
    assert response.status_code == 200
    assert response.json()["productName"] == "Updated Soda"


def test_delete_product():
    # Login as seller
    seller = {"username": "seller1", "password": "pass1"}
    client.post("/switch_user", json=seller)

    response = client.delete("/products/1")
    assert response.status_code == 200
    assert response.json() == {"productId": 1, "status": "deleted"}


def test_deposit_money():
    # Login as buyer
    buyer = {"username": "buyer1", "password": "pass2"}
    client.post("/switch_user", json=buyer)

    response = client.post("/deposit", json={"amount": 50})
    assert response.status_code == 200
    assert response.json()["total"] == 50


def test_invalid_deposit_money():
    # Login as buyer
    buyer = {"username": "buyer1", "password": "pass2"}
    client.post("/switch_user", json=buyer)

    response = client.post("/deposit", json={"amount": 7})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid coin value"}


def test_buy_product():
    # Login as buyer
    buyer = {"username": "buyer1", "password": "pass2"}
    client.post("/switch_user", json=buyer)

    # Deposit money
    client.post("/deposit", json={"amount": 100})

    # Purchase product
    response = client.post("/buy", json={"productId": 2, "amount": 1})
    assert response.status_code == 200
    assert response.json()["total_spent"] == 50
    assert response.json()["products_purchased"] == 1
    assert response.json()["change"] == {5: 0, 10: 0, 20: 2, 50: 0, 100: 0}


def test_buy_product_insufficient_deposit():
    # Login as buyer
    buyer = {"username": "buyer1", "password": "pass2"}
    client.post("/switch_user", json=buyer)

    # Deposit insufficient money
    client.post("/deposit", json={"amount": 20})

    # Attempt to purchase product
    response = client.post("/buy", json={"productId": 2, "amount": 1})
    assert response.status_code == 400
    assert response.json() == {"detail": "Not enough deposit"}


def test_reset_deposit():
    # Login as buyer
    buyer = {"username": "buyer1", "password": "pass2"}
    client.post("/switch_user", json=buyer)

    # Deposit money
    client.post("/deposit", json={"amount": 50})

    # Reset deposit
    response = client.post("/reset")
    assert response.status_code == 200
    assert response.json() == {"message": "Deposit reset successful"}


def test_switch_user():
    response = client.post("/switch_user", json={"username": "seller1", "password": "pass1"})
    assert response.status_code == 200
    assert response.json() == {"message": "Switched to user seller1"}


def test_invalid_switch_user():
    response = client.post("/switch_user", json={"username": "invalid_user", "password": "wrong_pass"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}
