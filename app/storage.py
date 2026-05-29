"""Хранилище задач в памяти (in-memory)."""
from __future__ import annotations

from .schemas import Task, TaskCreate, TaskStatus


class TaskStorage:
    """Простое потокобезопасное-для-тестов хранилище задач в памяти.

    Иммутабельность ответов обеспечивается тем, что наружу всегда отдаются
    новые объекты ``Task`` (Pydantic-модели), а внутренние данные не мутируются
    «на месте» вызывающим кодом.
    """

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def clear(self) -> None:
        """Полностью очистить хранилище (используется тестами)."""
        self._tasks = {}
        self._next_id = 1

    def create(self, owner_id: int, data: TaskCreate) -> Task:
        """Создать задачу для указанного владельца и вернуть её."""
        task = Task(
            id=self._next_id,
            title=data.title,
            description=data.description,
            status=data.status,
            priority=data.priority,
            owner_id=owner_id,
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def get(self, task_id: int) -> Task | None:
        """Вернуть задачу по идентификатору или ``None``."""
        return self._tasks.get(task_id)

    def list_for_owner(
        self,
        owner_id: int,
        status: TaskStatus | None = None,
        min_priority: int | None = None,
    ) -> list[Task]:
        """Вернуть задачи владельца с опциональной фильтрацией."""
        result = [t for t in self._tasks.values() if t.owner_id == owner_id]
        if status is not None:
            result = [t for t in result if t.status == status]
        if min_priority is not None:
            result = [t for t in result if t.priority >= min_priority]
        return sorted(result, key=lambda t: t.id)

    def all(self) -> list[Task]:
        """Вернуть все задачи (для админ-статистики)."""
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def update_status(self, task_id: int, status: TaskStatus) -> Task | None:
        """Обновить статус задачи, вернув новый объект задачи."""
        existing = self._tasks.get(task_id)
        if existing is None:
            return None
        updated = existing.model_copy(update={"status": status})
        self._tasks[task_id] = updated
        return updated

    def delete(self, task_id: int) -> bool:
        """Удалить задачу; вернуть ``True``, если она существовала."""
        return self._tasks.pop(task_id, None) is not None


# Singleton-хранилище, разделяемое всеми роутерами.
storage = TaskStorage()
