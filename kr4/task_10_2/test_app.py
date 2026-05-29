"""Тесты валидации и обработки ошибок (Задание 10.2)."""
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)

VALID_USER = {
    "username": "john_doe",
    "age": 25,
    "email": "john@example.com",
    "password": "secret123",
    "phone": "+79001234567",
}


def test_valid_user():
    response = client.post("/users", json=VALID_USER)
    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "john_doe"
    assert "password" not in body


def test_phone_defaults_to_unknown():
    payload = {k: v for k, v in VALID_USER.items() if k != "phone"}
    response = client.post("/users", json=payload)
    assert response.status_code == 200
    assert response.json()["phone"] == "Unknown"


def test_age_must_be_greater_than_18():
    payload = {**VALID_USER, "age": 18}
    response = client.post("/users", json=payload)
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert any(e["field"] == "age" for e in body["errors"])


def test_invalid_email():
    payload = {**VALID_USER, "email": "not-an-email"}
    response = client.post("/users", json=payload)
    assert response.status_code == 422
    assert any(e["field"] == "email" for e in response.json()["errors"])


def test_password_too_short():
    payload = {**VALID_USER, "password": "short"}
    response = client.post("/users", json=payload)
    assert response.status_code == 422
    assert any(e["field"] == "password" for e in response.json()["errors"])


def test_multiple_errors_reported_together():
    payload = {"username": "x", "age": 5, "email": "bad", "password": "1"}
    response = client.post("/users", json=payload)
    assert response.status_code == 422
    fields = {e["field"] for e in response.json()["errors"]}
    assert {"age", "email", "password"} <= fields
