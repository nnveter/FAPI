"""FastAPI-зависимости: аутентификация, проверка прав, доступ к хранилищу."""
from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status

from .schemas import User
from .storage import TaskStorage, storage


def get_current_user(
    x_user_id: str | None = Header(default=None),
    x_user_role: str | None = Header(default=None),
) -> User:
    """Восстановить текущего пользователя из заголовков запроса.

    Считывает ``X-User-Id`` (обязателен, должен приводиться к ``int``) и
    ``X-User-Role`` (по умолчанию ``user``). При отсутствии или некорректном
    ``X-User-Id`` возвращает 401.
    """
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Id header",
        )
    try:
        user_id = int(x_user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid X-User-Id header",
        )
    role = (x_user_role or "user").strip() or "user"
    return User(id=user_id, role=role)


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Разрешить доступ только пользователям с ролью ``admin`` (иначе 403)."""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return user


def get_storage() -> TaskStorage:
    """Вернуть singleton-хранилище задач."""
    return storage
