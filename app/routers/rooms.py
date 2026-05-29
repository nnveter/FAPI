"""Маршрутизатор WebSocket-комнат и HTTP-просмотра участников."""
from __future__ import annotations

from fastapi import (
    APIRouter,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)

from ..schemas import RoomUsers
from ..ws_manager import manager

MAX_MESSAGE_LENGTH = 300

# HTTP-маршрутизатор для просмотра активных пользователей комнаты.
http_router = APIRouter(prefix="/rooms", tags=["rooms"])

# Отдельный роутер для WebSocket-маршрута.
ws_router = APIRouter(tags=["rooms"])


@http_router.get("/{room_id}/users", response_model=RoomUsers)
def room_users(room_id: str) -> RoomUsers:
    """Вернуть список активных пользователей указанной комнаты."""
    return RoomUsers(room_id=room_id, users=manager.get_users(room_id))


@ws_router.websocket("/ws/rooms/{room_id}")
async def room_socket(
    websocket: WebSocket,
    room_id: str,
    username: str | None = Query(default=None),
) -> None:
    """WebSocket-чат комнаты.

    Подключает пользователя, рассылает события входа/выхода и сообщения.
    При пустом ``username`` соединение закрывается с кодом 1008.
    """
    if username is None or not username.strip():
        await websocket.accept()
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    username = username.strip()
    await manager.connect(room_id, username, websocket)
    await manager.broadcast(
        room_id,
        {"type": "join", "room_id": room_id, "username": username},
    )

    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") != "message":
                continue
            text = data.get("text", "")
            if not isinstance(text, str):
                text = str(text)
            if len(text) > MAX_MESSAGE_LENGTH:
                await websocket.send_json(
                    {"type": "error", "detail": "Message is too long"}
                )
                continue
            await manager.broadcast(
                room_id,
                {
                    "type": "message",
                    "room_id": room_id,
                    "username": username,
                    "text": text,
                },
            )
    except WebSocketDisconnect:
        manager.disconnect(room_id, username, websocket)
        await manager.broadcast(
            room_id,
            {"type": "leave", "room_id": room_id, "username": username},
        )
