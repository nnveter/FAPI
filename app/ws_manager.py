"""Менеджер WebSocket-комнат для чата."""
from __future__ import annotations

from fastapi import WebSocket


class RoomManager:
    """Управляет подключениями WebSocket, сгруппированными по комнатам."""

    def __init__(self) -> None:
        # room_id -> список пар (username, websocket)
        self._rooms: dict[str, list[tuple[str, WebSocket]]] = {}

    async def connect(self, room_id: str, username: str, websocket: WebSocket) -> None:
        """Принять соединение и добавить пользователя в комнату."""
        await websocket.accept()
        self._rooms.setdefault(room_id, []).append((username, websocket))

    def disconnect(self, room_id: str, username: str, websocket: WebSocket) -> None:
        """Удалить конкретное соединение пользователя из комнаты."""
        connections = self._rooms.get(room_id)
        if not connections:
            return
        self._rooms[room_id] = [
            (name, ws)
            for (name, ws) in connections
            if not (name == username and ws is websocket)
        ]
        if not self._rooms[room_id]:
            del self._rooms[room_id]

    async def broadcast(self, room_id: str, payload: dict) -> None:
        """Отправить JSON-сообщение всем участникам комнаты."""
        for _name, ws in list(self._rooms.get(room_id, [])):
            await ws.send_json(payload)

    def get_users(self, room_id: str) -> list[str]:
        """Вернуть список уникальных имён активных пользователей комнаты."""
        seen: list[str] = []
        for name, _ws in self._rooms.get(room_id, []):
            if name not in seen:
                seen.append(name)
        return seen

    def clear(self) -> None:
        """Очистить все комнаты (используется тестами)."""
        self._rooms = {}


# Singleton-менеджер, разделяемый WebSocket-маршрутами.
manager = RoomManager()
