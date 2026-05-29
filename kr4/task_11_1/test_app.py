"""Модульные тесты приложения (Задание 11.1).

Используется pytest + fastapi.testclient.TestClient.
Тесты сгруппированы по эндпоинтам в классы для читаемости.
"""
import pytest
from fastapi.testclient import TestClient

from app import app, reset_state

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_state():
    """Чистое состояние хранилища до и после каждого теста (изоляция)."""
    reset_state()
    yield
    reset_state()


class TestHealth:
    def test_health_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestCreateTodo:
    def test_create_returns_201_and_structure(self):
        response = client.post("/todos", json={"title": "Buy milk"})
        assert response.status_code == 201
        body = response.json()
        assert body == {"id": 1, "title": "Buy milk", "done": False}

    def test_create_with_invalid_title_returns_422(self):
        response = client.post("/todos", json={"title": ""})
        assert response.status_code == 422

    def test_ids_are_incremental(self):
        first = client.post("/todos", json={"title": "a"}).json()
        second = client.post("/todos", json={"title": "b"}).json()
        assert first["id"] == 1
        assert second["id"] == 2


class TestGetTodo:
    def test_get_existing_todo(self):
        created = client.post("/todos", json={"title": "Read book"}).json()
        response = client.get(f"/todos/{created['id']}")
        assert response.status_code == 200
        assert response.json() == created

    def test_get_missing_todo_returns_404(self):
        response = client.get("/todos/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Todo not found"


class TestListTodos:
    def test_list_empty(self):
        response = client.get("/todos")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_after_inserts(self):
        client.post("/todos", json={"title": "a"})
        client.post("/todos", json={"title": "b"})
        response = client.get("/todos")
        assert len(response.json()) == 2


class TestDeleteTodo:
    def test_delete_existing_returns_204(self):
        created = client.post("/todos", json={"title": "temp"}).json()
        response = client.delete(f"/todos/{created['id']}")
        assert response.status_code == 204
        # Повторное чтение — уже 404.
        assert client.get(f"/todos/{created['id']}").status_code == 404

    def test_delete_missing_returns_404(self):
        response = client.delete("/todos/999")
        assert response.status_code == 404
