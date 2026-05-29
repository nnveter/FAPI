"""Админ-маршрутизатор (префикс /admin)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status

from ..dependencies import get_storage, require_admin
from ..schemas import AdminStats, StatusCount, TaskStatus, User
from ..storage import TaskStorage

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStats)
def get_stats(
    _admin: User = Depends(require_admin),
    storage: TaskStorage = Depends(get_storage),
) -> AdminStats:
    """Вернуть агрегированную статистику по всем задачам."""
    tasks = storage.all()
    counts = StatusCount()
    for task in tasks:
        if task.status == TaskStatus.todo:
            counts.todo += 1
        elif task.status == TaskStatus.in_progress:
            counts.in_progress += 1
        elif task.status == TaskStatus.done:
            counts.done += 1
    return AdminStats(total_tasks=len(tasks), by_status=counts)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_any_task(
    task_id: int,
    _admin: User = Depends(require_admin),
    storage: TaskStorage = Depends(get_storage),
) -> Response:
    """Удалить любую задачу независимо от владельца."""
    if not storage.delete(task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
