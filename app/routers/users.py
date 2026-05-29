"""Маршрутизатор пользователей (префикс /users)."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ..dependencies import get_current_user
from ..schemas import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
def get_me(user: User = Depends(get_current_user)) -> User:
    """Вернуть текущего аутентифицированного пользователя."""
    return user


@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: int,
    current: User = Depends(get_current_user),
) -> User:
    """Вернуть пользователя по идентификатору.

    Хранилища пользователей нет, поэтому возвращается объект на основе
    переданного ``user_id``. Если запрашивается собственный профиль —
    отдаётся реальная роль текущего пользователя.
    """
    if user_id == current.id:
        return current
    return User(id=user_id, role="user")
