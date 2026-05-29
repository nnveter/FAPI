"""Маршрутизатор управления задачами (префикс /tasks)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from ..dependencies import get_current_user, get_storage
from ..schemas import Task, TaskCreate, TaskStatus, TaskStatusUpdate, User
from ..storage import TaskStorage

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _get_owned_task(storage: TaskStorage, task_id: int, user: User) -> Task:
    """Вернуть задачу, принадлежащую пользователю, иначе 404."""
    task = storage.get(task_id)
    if task is None or task.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Task)
def create_task(
    payload: TaskCreate,
    user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
) -> Task:
    """Создать задачу для текущего пользователя."""
    return storage.create(owner_id=user.id, data=payload)


@router.get("", response_model=list[Task])
def list_tasks(
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    min_priority: int | None = Query(default=None, ge=1, le=5),
    user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
) -> list[Task]:
    """Вернуть задачи текущего пользователя с опциональной фильтрацией."""
    return storage.list_for_owner(
        owner_id=user.id, status=status_filter, min_priority=min_priority
    )


@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
) -> Task:
    """Вернуть одну задачу текущего пользователя."""
    return _get_owned_task(storage, task_id, user)


@router.patch("/{task_id}/status", response_model=Task)
def update_task_status(
    task_id: int,
    payload: TaskStatusUpdate,
    user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
) -> Task:
    """Изменить статус задачи текущего пользователя."""
    _get_owned_task(storage, task_id, user)
    updated = storage.update_status(task_id, payload.status)
    assert updated is not None  # задача проверена выше
    return updated


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
) -> Response:
    """Удалить задачу текущего пользователя."""
    _get_owned_task(storage, task_id, user)
    storage.delete(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
