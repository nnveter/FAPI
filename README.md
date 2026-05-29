# КР5 — Технологии разработки серверных приложений

FastAPI-приложение, объединяющее четыре задания контрольной работы №5:

1. **REST API задач** с имитацией авторизации через заголовок `X-User-Id`.
2. **Docker-контейнеризация** (Dockerfile + docker-compose) и маршрут `/health`.
3. **WebSocket-комнаты** для чата с рассылкой сообщений и просмотром участников.
4. **Внедрение зависимостей и расширенная маршрутизация** (`APIRouter`,
   роли `user`/`admin`, проверка прав доступа).

## Структура проекта

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # точка входа, сборка приложения, /health
│   ├── dependencies.py      # get_current_user, require_admin, get_storage
│   ├── schemas.py           # Pydantic-модели и перечисления
│   ├── storage.py           # in-memory хранилище задач (singleton)
│   ├── ws_manager.py        # RoomManager для WebSocket-комнат
│   └── routers/
│       ├── __init__.py
│       ├── tasks.py         # /tasks  (требует get_current_user)
│       ├── users.py         # /users/me, /users/{user_id}
│       ├── admin.py         # /admin  (требует require_admin)
│       └── rooms.py         # /ws/rooms/{room_id}, /rooms/{room_id}/users
├── tests/
│   ├── conftest.py
│   ├── test_tasks.py
│   ├── test_websocket.py
│   ├── test_dependencies_and_routing.py
│   └── test_health.py
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── requirements.txt
├── pytest.ini
└── README.md
```

## Требования

- Python 3.12 (для локального запуска) или Docker.

## Запуск локально через uvicorn

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Приложение будет доступно на http://localhost:8000.
Документация Swagger UI — http://localhost:8000/docs (маршруты сгруппированы по
тегам `tasks`, `users`, `admin`, `rooms`, `health`).

## Запуск тестов

```bash
pytest
```

Тесты покрывают:

- создание/чтение/фильтрацию/обновление/удаление задач и коды 401/404/422;
- маршрут `/health`;
- WebSocket-комнаты (подключение, рассылка, изоляция комнат, длинные сообщения,
  обновление списка участников после отключения);
- зависимости и проверку прав (`/users/me`, доступ к `/admin/*`, удаление чужих
  задач, группировку по тегам в Swagger).

## Запуск в Docker

```bash
docker compose up --build
```

Сервис `api` собирается из текущей директории, пробрасывает порт `8000:8000`,
передаёт переменную окружения `APP_ENV=docker` и перезапускается с политикой
`unless-stopped`.

Проверка после запуска:

```bash
curl http://localhost:8000/tasks -H "X-User-Id: 10"
# []

curl http://localhost:8000/health
# {"status":"ok","env":"docker"}
```

## Авторизация (имитация)

Все маршруты `/tasks`, `/users` и `/admin` требуют заголовков:

| Заголовок     | Обязательность | Описание                              |
|---------------|----------------|---------------------------------------|
| `X-User-Id`   | да             | идентификатор пользователя (`int`)    |
| `X-User-Role` | нет            | роль: `user` (по умолчанию) / `admin` |

Если `X-User-Id` отсутствует или не приводится к `int` — ответ `401`.
Для админ-маршрутов при роли, отличной от `admin`, — ответ `403`.

## Основные маршруты

### Задачи (`tasks`)

| Метод  | Маршрут                     | Успех | Описание                          |
|--------|-----------------------------|-------|-----------------------------------|
| POST   | `/tasks`                    | 201   | создать задачу                    |
| GET    | `/tasks`                    | 200   | список своих задач (`status`, `min_priority`) |
| GET    | `/tasks/{task_id}`          | 200   | одна своя задача (иначе 404)      |
| PATCH  | `/tasks/{task_id}/status`   | 200   | изменить статус                   |
| DELETE | `/tasks/{task_id}`          | 204   | удалить свою задачу               |

### Пользователи (`users`)

| Метод | Маршрут             | Описание                       |
|-------|---------------------|--------------------------------|
| GET   | `/users/me`         | текущий пользователь           |
| GET   | `/users/{user_id}`  | пользователь по идентификатору |

### Админ (`admin`, только роль `admin`)

| Метод  | Маршрут                    | Описание                          |
|--------|----------------------------|-----------------------------------|
| GET    | `/admin/stats`             | статистика по всем задачам        |
| DELETE | `/admin/tasks/{task_id}`   | удалить любую задачу (204 / 404)  |

### Комнаты (`rooms`)

| Метод     | Маршрут                                | Описание                              |
|-----------|----------------------------------------|---------------------------------------|
| WebSocket | `/ws/rooms/{room_id}?username=alice`   | подключение к комнате чата            |
| GET       | `/rooms/{room_id}/users`               | список активных участников комнаты     |

Формат сообщения от клиента:

```json
{ "type": "message", "text": "Всем привет" }
```

Рассылка сервера:

```json
{ "type": "message", "room_id": "python", "username": "alice", "text": "Всем привет" }
```

Если `username` пустой — соединение закрывается с кодом `1008`.
Сообщение длиннее 300 символов — отправителю приходит
`{ "type": "error", "detail": "Message is too long" }`.
