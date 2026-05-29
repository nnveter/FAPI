"""Интеграционные тесты для API задач (Задание 1)."""
from __future__ import annotations

from fastapi.testclient import TestClient

USER_10 = {"X-User-Id": "10"}
USER_20 = {"X-User-Id": "20"}


def _make_task(client: TestClient, headers: dict, **overrides) -> dict:
    payload = {
        "title": "Подготовить тесты",
        "description": "Написать интеграционные тесты для основных сценариев",
        "status": "todo",
        "priority": 4,
    }
    payload.update(overrides)
    response = client.post("/tasks", json=payload, headers=headers)
    return response


def test_create_task_success(client: TestClient) -> None:
    response = _make_task(client, USER_10)
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["title"] == "Подготовить тесты"
    assert body["status"] == "todo"
    assert body["priority"] == 4
    assert body["owner_id"] == 10


def test_create_task_title_too_short_returns_422(client: TestClient) -> None:
    response = _make_task(client, USER_10, title="ab")
    assert response.status_code == 422


def test_create_task_without_header_returns_401(client: TestClient) -> None:
    response = client.post(
        "/tasks",
        json={"title": "Заголовок задачи", "priority": 3, "status": "todo"},
    )
    assert response.status_code == 401


def test_invalid_user_id_returns_401(client: TestClient) -> None:
    response = client.get("/tasks", headers={"X-User-Id": "abc"})
    assert response.status_code == 401


def test_user_sees_only_own_tasks(client: TestClient) -> None:
    _make_task(client, USER_10, title="Задача десятого")
    _make_task(client, USER_20, title="Задача двадцатого")

    response = client.get("/tasks", headers=USER_10)
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["owner_id"] == 10


def test_filter_by_status_and_min_priority(client: TestClient) -> None:
    _make_task(client, USER_10, title="Первая", status="todo", priority=2)
    _make_task(client, USER_10, title="Вторая", status="done", priority=5)
    _make_task(client, USER_10, title="Третья", status="done", priority=1)

    by_status = client.get("/tasks", params={"status": "done"}, headers=USER_10)
    assert {t["title"] for t in by_status.json()} == {"Вторая", "Третья"}

    by_priority = client.get(
        "/tasks", params={"min_priority": 3}, headers=USER_10
    )
    assert {t["title"] for t in by_priority.json()} == {"Вторая"}

    combined = client.get(
        "/tasks",
        params={"status": "done", "min_priority": 3},
        headers=USER_10,
    )
    assert {t["title"] for t in combined.json()} == {"Вторая"}


def test_update_status_success(client: TestClient) -> None:
    created = _make_task(client, USER_10).json()
    response = client.patch(
        f"/tasks/{created['id']}/status",
        json={"status": "done"},
        headers=USER_10,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_get_foreign_or_missing_task_returns_404(client: TestClient) -> None:
    created = _make_task(client, USER_10).json()

    foreign = client.get(f"/tasks/{created['id']}", headers=USER_20)
    assert foreign.status_code == 404

    missing = client.get("/tasks/99999", headers=USER_10)
    assert missing.status_code == 404


def test_delete_task_success(client: TestClient) -> None:
    created = _make_task(client, USER_10).json()
    response = client.delete(f"/tasks/{created['id']}", headers=USER_10)
    assert response.status_code == 204

    after = client.get(f"/tasks/{created['id']}", headers=USER_10)
    assert after.status_code == 404
