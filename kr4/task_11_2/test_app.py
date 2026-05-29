"""Асинхронные модульные тесты (Задание 11.2).

Стек: pytest-asyncio + httpx.AsyncClient через ASGITransport + Faker.
Запросы идут в приложение напрямую (ASGI), без запуска Uvicorn.
"""
import pytest
import pytest_asyncio
from faker import Faker
from httpx import ASGITransport, AsyncClient

from app import app, reset_state

faker = Faker()


@pytest.fixture(autouse=True)
def isolate_state():
    """Чистое состояние in-memory хранилища до и после каждого теста."""
    reset_state()
    yield
    reset_state()


@pytest_asyncio.fixture
async def client():
    """AsyncClient поверх ASGITransport — обращается к app напрямую."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def fake_user() -> dict:
    """Реалистичные валидные данные пользователя через Faker."""
    return {"username": faker.user_name(), "age": faker.random_int(min=18, max=99)}


class TestCreateUser:
    @pytest.mark.asyncio
    async def test_create_user_201_and_structure(self, client: AsyncClient):
        payload = fake_user()
        response = await client.post("/users", json=payload)
        assert response.status_code == 201
        body = response.json()
        assert body["id"] == 1
        assert body["username"] == payload["username"]
        assert body["age"] == payload["age"]

    @pytest.mark.asyncio
    async def test_create_user_boundary_age(self, client: AsyncClient):
        # Граничные значения возраста.
        for age in (0, 18, 150):
            response = await client.post(
                "/users", json={"username": faker.user_name(), "age": age}
            )
            assert response.status_code == 201
            assert response.json()["age"] == age


class TestGetUser:
    @pytest.mark.asyncio
    async def test_get_existing_user_200(self, client: AsyncClient):
        created = (await client.post("/users", json=fake_user())).json()
        response = await client.get(f"/users/{created['id']}")
        assert response.status_code == 200
        assert response.json() == created

    @pytest.mark.asyncio
    async def test_get_missing_user_404(self, client: AsyncClient):
        response = await client.get("/users/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"


class TestDeleteUser:
    @pytest.mark.asyncio
    async def test_delete_existing_user_204(self, client: AsyncClient):
        created = (await client.post("/users", json=fake_user())).json()
        response = await client.delete(f"/users/{created['id']}")
        assert response.status_code == 204
        # Пользователь действительно удалён.
        assert (await client.get(f"/users/{created['id']}")).status_code == 404

    @pytest.mark.asyncio
    async def test_delete_same_user_twice_404(self, client: AsyncClient):
        created = (await client.post("/users", json=fake_user())).json()
        first = await client.delete(f"/users/{created['id']}")
        second = await client.delete(f"/users/{created['id']}")
        assert first.status_code == 204
        assert second.status_code == 404
