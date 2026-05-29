"""Тесты обработки пользовательских исключений (Задание 10.1)."""
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_divide_ok():
    response = client.get("/divide", params={"a": 10, "b": 2})
    assert response.status_code == 200
    assert response.json() == {"result": 5.0}


def test_divide_raises_custom_exception_a():
    response = client.get("/divide", params={"a": 10, "b": 0})
    assert response.status_code == 418
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "CONDITION_NOT_MET"
    assert body["message"] == "Делить на ноль нельзя"


def test_get_item_ok():
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "apple"}


def test_get_item_raises_custom_exception_b():
    response = client.get("/items/999")
    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "RESOURCE_NOT_FOUND"
    assert "999" in body["message"]
