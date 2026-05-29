"""Pydantic-схемы и доменные перечисления приложения."""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Допустимые статусы задачи."""

    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class TaskCreate(BaseModel):
    """Тело запроса для создания задачи."""

    title: str = Field(min_length=3, max_length=80)
    description: str | None = None
    status: TaskStatus = TaskStatus.todo
    priority: int = Field(ge=1, le=5)


class TaskStatusUpdate(BaseModel):
    """Тело запроса для изменения статуса задачи."""

    status: TaskStatus


class Task(BaseModel):
    """Полное представление задачи в ответах API."""

    id: int
    title: str
    description: str | None = None
    status: TaskStatus
    priority: int
    owner_id: int


class User(BaseModel):
    """Текущий пользователь, восстановленный из заголовков запроса."""

    id: int
    role: str = "user"


class HealthResponse(BaseModel):
    """Ответ маршрута проверки состояния приложения."""

    status: str
    env: str


class StatusCount(BaseModel):
    """Счётчики задач по статусам для админ-статистики."""

    todo: int = 0
    in_progress: int = 0
    done: int = 0


class AdminStats(BaseModel):
    """Агрегированная статистика по всем задачам."""

    total_tasks: int
    by_status: StatusCount


class RoomUsers(BaseModel):
    """Список активных пользователей комнаты."""

    room_id: str
    users: list[str]
