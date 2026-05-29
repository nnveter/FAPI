# KR4 — Миграции, обработка ошибок и тестирование (FastAPI)

Контрольная работа №4 по дисциплине «Технологии разработки серверных приложений».

## Структура

```
kr4/
├── task_9_1/    # Alembic: миграции БД + модель Product (SQLAlchemy)
├── task_10_1/   # Пользовательские исключения и обработчики ошибок
├── task_10_2/   # Валидация данных запроса + обработка ошибок валидации
├── task_11_1/   # Модульные тесты (pytest + TestClient)
└── task_11_2/   # Асинхронные тесты (pytest-asyncio + httpx + Faker)
```

## Установка зависимостей

```bash
pip install -r requirements.txt
```

Рекомендуется виртуальное окружение:

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Linux/macOS
source .venv/bin/activate
pip install -r requirements.txt
```

## Запуск приложений

Каждое задание — самостоятельное FastAPI-приложение. Перейдите в каталог задания
и запустите Uvicorn:

```bash
cd task_10_1
uvicorn app:app --reload
```

Интерактивная документация (Swagger UI) — на `http://localhost:8000/docs`.

---

## Task 9.1 — Alembic: миграции и модель Product

Модель `Product` (`models.py`): `id`, `title`, `price`, `count`, `description`.
История схемы отражена двумя миграциями Alembic:

1. `create products table` — создаёт таблицу с полями `id, title, price, count`;
2. `add description to products` — добавляет NOT NULL поле `description`.

БД по умолчанию — SQLite (`sqlite:///./products.db`). URL можно переопределить
переменной окружения `DATABASE_URL` (см. `.env.example`).

### Применение миграций и проверка

```bash
cd task_9_1

# Применить все миграции (создаст таблицу products со всеми полями)
python -m alembic upgrade head

# Добавить две записи в таблицу (шаг 5 задания)
python seed.py

# Посмотреть историю миграций
python -m alembic history

# Текущая ревизия
python -m alembic current
```

Как воспроизвести полный сценарий задания (миграция 1 → данные → миграция 2):

```bash
# Применить только первую миграцию
python -m alembic upgrade 80b672298fbf
# ... добавить записи ...
# Применить вторую миграцию
python -m alembic upgrade head
# Откатить последнюю миграцию (демонстрация downgrade)
python -m alembic downgrade -1
```

Запуск приложения с CRUD по продуктам:

```bash
uvicorn app:app --reload
# POST /products, GET /products, GET /products/{id}
```

---

## Task 10.1 — Пользовательская обработка ошибок

Два пользовательских исключения с уникальными кодами состояния:

- `CustomExceptionA` → `418`, `error_code=CONDITION_NOT_MET`;
- `CustomExceptionB` → `404`, `error_code=RESOURCE_NOT_FOUND`.

Для каждого зарегистрирован обработчик (`@app.exception_handler`), формат ответа
описан Pydantic-моделью `ErrorResponse` (`success`, `error_code`, `message`).

### Проверка функциональности

```bash
cd task_10_1
uvicorn app:app --reload
```

```bash
# Успех
curl "http://localhost:8000/divide?a=10&b=2"

# CustomExceptionA → 418
curl -i "http://localhost:8000/divide?a=10&b=0"

# Успех
curl http://localhost:8000/items/1

# CustomExceptionB → 404
curl -i http://localhost:8000/items/999
```

---

## Task 10.2 — Валидация данных запроса

Модель `User` (Pydantic) с ограничениями: `username: str`, `age > 18`,
`email: EmailStr`, `password` (длина 8–16), `phone: Optional[str] = "Unknown"`.
Ошибки валидации перехватываются обработчиком `RequestValidationError` и
возвращаются в едином формате (`ValidationErrorResponse`) с кодом `422`.

### Проверка функциональности

```bash
cd task_10_2
uvicorn app:app --reload
```

```bash
# Валидный пользователь → 200
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username":"john","age":25,"email":"john@example.com","password":"secret123"}'

# Невалидные данные → 422 с подробным списком ошибок по полям
curl -i -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username":"x","age":5,"email":"bad","password":"1"}'
```

---

## Task 11.1 — Модульные тесты (синхронные)

Приложение с CRUD-эндпоинтами для todo (`/health`, `/todos`, `/todos/{id}`).
Тесты используют `fastapi.testclient.TestClient`, сгруппированы в классы,
изоляция состояния обеспечивается фикстурой `reset_state`.

---

## Task 11.2 — Асинхронные тесты

Приложение с тремя эндпоинтами (`POST/GET/DELETE /users`) и in-memory
хранилищем. Тесты асинхронные (`pytest-asyncio`), идут в приложение напрямую
через `httpx.AsyncClient` + `ASGITransport` (без запуска Uvicorn), входные
данные генерируются библиотекой **Faker**. Покрыты сценарии: создание (201),
получение (200/404), удаление (204) и повторное удаление (404).

---

## Тестирование ключевых сценариев

Тесты запускаются **из каталога конкретного задания** (у заданий совпадают имена
файлов `test_app.py`, поэтому общий запуск из корня делать не нужно):

```bash
# Task 10.1 — обработка пользовательских исключений
cd task_10_1 && python -m pytest -v

# Task 10.2 — валидация и ошибки валидации
cd task_10_2 && python -m pytest -v

# Task 11.1 — синхронные модульные тесты (TestClient)
cd task_11_1 && python -m pytest -v

# Task 11.2 — асинхронные тесты (pytest-asyncio + httpx + Faker)
cd task_11_2 && python -m pytest -v
```

Все тесты должны завершаться статусом **passed**.

## Переменные окружения

Используются только в `task_9_1` (`DATABASE_URL`). Шаблон — `task_9_1/.env.example`.
Реальный `.env` в репозиторий не коммитится (см. `.gitignore`).
