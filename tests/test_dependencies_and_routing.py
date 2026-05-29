"""Тесты зависимостей и расширенной маршрутизации (Задание 4)."""
from __future__ import annotations

from fastapi.testclient import TestClient

USER = {"X-User-Id": "10", "X-User-Role": "user"}
OTHER_USER = {"X-User-Id": "20", "X-User-Role": "user"}
ADMIN = {"X-User-Id": "1", "X-User-Role": "admin"}


def _create(client: TestClient, headers: dict, **overrides) -> dict:
    payload = {"title": "Базовая задача", "priority": 3, "status": "todo"}
    payload.update(overrides)
    return client.post("/tasks", json=payload, headers=headers).json()


def test_users_me_returns_current_user(client: TestClient) -> None:
    response = client.get("/users/me", headers=USER)
    assert response.status_code == 200
    assert response.json() == {"id": 10, "role": "user"}


def test_no_header_returns_401(client: TestClient) -> None:
    assert client.get("/users/me").status_code == 401


def test_regular_user_forbidden_on_admin_stats(client: TestClient) -> None:
    response = client.get("/admin/stats", headers=USER)
    assert response.status_code == 403


def test_admin_gets_stats_for_all_tasks(client: TestClient) -> None:
    _create(client, USER, status="todo")
    _create(client, USER, status="in_progress")
    _create(client, OTHER_USER, status="done")
    _create(client, OTHER_USER, status="done")

    response = client.get("/admin/stats", headers=ADMIN)
    assert response.status_code == 200
    body = response.json()
    assert body["total_tasks"] == 4
    assert body["by_status"] == {"todo": 1, "in_progress": 1, "done": 2}


def test_user_cannot_delete_foreign_task_via_tasks(client: TestClient) -> None:
    foreign = _create(client, OTHER_USER)
    response = client.delete(f"/tasks/{foreign['id']}", headers=USER)
    assert response.status_code == 404


def test_admin_can_delete_foreign_task_via_admin(client: TestClient) -> None:
    foreign = _create(client, OTHER_USER)
    response = client.delete(f"/admin/tasks/{foreign['id']}", headers=ADMIN)
    assert response.status_code == 204
    # Задача действительно удалена.
    assert client.get(f"/tasks/{foreign['id']}", headers=OTHER_USER).status_code == 404


def test_admin_delete_missing_task_returns_404(client: TestClient) -> None:
    assert client.delete("/admin/tasks/99999", headers=ADMIN).status_code == 404


def test_swagger_groups_routes_by_tags(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    tags = {
        tag
        for path in schema["paths"].values()
        for method in path.values()
        for tag in method.get("tags", [])
    }
    assert {"tasks", "users", "admin"}.issubset(tags)
