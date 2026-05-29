"""Общие фикстуры для интеграционных тестов."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import storage
from app.ws_manager import manager


@pytest.fixture
def client() -> TestClient:
    """TestClient для приложения."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_state() -> None:
    """Очищать хранилище задач и комнаты перед каждым тестом."""
    storage.clear()
    manager.clear()
    yield
    storage.clear()
    manager.clear()
