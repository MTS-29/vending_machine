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


def test_switch_user():
    response = client.post("/switch_user", json={"username": "seller1", "password": "pass1"})
    assert response.status_code == 200
    assert response.json() == {"message": "Switched to user seller1"}


def test_invalid_switch_user():
    response = client.post("/switch_user", json={"username": "invalid_user", "password": "wrong_pass"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}
