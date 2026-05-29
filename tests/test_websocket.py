"""Тесты WebSocket-комнат (Задание 3)."""
from __future__ import annotations

from fastapi.testclient import TestClient


def test_connect_with_valid_username_receives_join(client: TestClient) -> None:
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        event = ws.receive_json()
        assert event["type"] == "join"
        assert event["room_id"] == "python"
        assert event["username"] == "alice"


def test_connect_without_username_is_rejected(client: TestClient) -> None:
    with client.websocket_connect("/ws/rooms/python") as ws:
        # Сервер закрывает соединение с кодом 1008; чтение вызывает закрытие.
        import pytest
        from starlette.websockets import WebSocketDisconnect

        with pytest.raises(WebSocketDisconnect) as exc:
            ws.receive_json()
        assert exc.value.code == 1008


def test_send_and_receive_message(client: TestClient) -> None:
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()  # join
        ws.send_json({"type": "message", "text": "Всем привет"})
        msg = ws.receive_json()
        assert msg["type"] == "message"
        assert msg["room_id"] == "python"
        assert msg["username"] == "alice"
        assert msg["text"] == "Всем привет"


def test_two_clients_same_room_receive_message(client: TestClient) -> None:
    with client.websocket_connect("/ws/rooms/python?username=alice") as a, \
            client.websocket_connect("/ws/rooms/python?username=bob") as b:
        # alice: свой join + join bob; bob: свой join
        a.receive_json()
        a.receive_json()
        b.receive_json()

        a.send_json({"type": "message", "text": "Привет, комната"})

        msg_a = a.receive_json()
        msg_b = b.receive_json()
        assert msg_a == msg_b
        assert msg_b["text"] == "Привет, комната"
        assert msg_b["username"] == "alice"


def test_clients_in_different_rooms_are_isolated(client: TestClient) -> None:
    with client.websocket_connect("/ws/rooms/python?username=alice") as a, \
            client.websocket_connect("/ws/rooms/java?username=bob") as b:
        a.receive_json()  # join alice
        b.receive_json()  # join bob

        a.send_json({"type": "message", "text": "только для python"})
        msg_a = a.receive_json()
        assert msg_a["text"] == "только для python"

        # bob отправляет своё, чтобы убедиться, что приходит только его сообщение.
        b.send_json({"type": "message", "text": "только для java"})
        msg_b = b.receive_json()
        assert msg_b["text"] == "только для java"
        assert msg_b["room_id"] == "java"


def test_too_long_message_returns_error(client: TestClient) -> None:
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()  # join
        ws.send_json({"type": "message", "text": "x" * 301})
        err = ws.receive_json()
        assert err["type"] == "error"
        assert err["detail"] == "Message is too long"


def test_users_list_updates_after_disconnect(client: TestClient) -> None:
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()  # join
        resp = client.get("/rooms/python/users")
        assert resp.status_code == 200
        assert resp.json() == {"room_id": "python", "users": ["alice"]}

    # После выхода из контекста соединение закрыто.
    resp_after = client.get("/rooms/python/users")
    assert "alice" not in resp_after.json()["users"]
