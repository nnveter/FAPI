# KR3 — Аутентификация, авторизация и база данных (FastAPI)

Контрольная работа №3 по дисциплине «Технологии разработки серверных приложений».

## Структура

```
kr3/
├── task_6_1/   # Basic HTTP-аутентификация
├── task_6_2/   # Хэширование паролей (bcrypt) + защита от timing-атак
├── task_6_3/   # Управление документацией через переменные окружения
├── task_6_4/   # JWT-аутентификация
├── task_6_5/   # JWT + регистрация + rate limiting (slowapi)
├── task_7_1/   # RBAC (role-based access control)
├── task_8_1/   # SQLite: таблица users, регистрация (raw SQL)
└── task_8_2/   # SQLite: полный CRUD для Todo (raw SQL)
```

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Запуск

Перейдите в нужную директорию задания и запустите:

```bash
uvicorn app:app --reload
```

Для **task_6_3** сначала скопируйте `.env.example` в `.env` и при необходимости измените значения:

```bash
cp task_6_3/.env.example task_6_3/.env
cd task_6_3
uvicorn app:app --reload
```

---

## Тестирование эндпоинтов

### Task 6.1 — Basic Auth

```bash
# Неверные данные → 401
curl -u wrong:pass http://localhost:8000/login

# Верные данные → 200
curl -u admin:secret123 http://localhost:8000/login
```

### Task 6.2 — Регистрация + bcrypt

```bash
# Регистрация пользователя
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "correctpass"}'

# Вход с верным паролем
curl -u user1:correctpass http://localhost:8000/login

# Вход с неверным паролем → 401
curl -u user1:wrongpass http://localhost:8000/login
```

### Task 6.3 — Документация через ENV

Переменные окружения (`.env`):
```
MODE=DEV          # DEV — docs защищены паролем, PROD — возвращают 404
DOCS_USER=admin
DOCS_PASSWORD=secret
```

```bash
# DEV: открыть /docs с авторизацией
curl -u admin:secret http://localhost:8000/docs

# Проверка работоспособности
curl http://localhost:8000/health
```

### Task 6.4 — JWT

```bash
# Получить токен
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "password123"}'

# Обратиться к защищённому ресурсу
curl http://localhost:8000/protected_resource \
  -H "Authorization: Bearer <access_token>"
```

### Task 6.5 — Регистрация + JWT + rate limiting

```bash
# Регистрация (лимит: 1 запрос/мин)
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "pass123"}'

# Вход (лимит: 5 запросов/мин)
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "pass123"}'

# Защищённый ресурс
curl http://localhost:8000/protected_resource \
  -H "Authorization: Bearer <access_token>"
```

### Task 7.1 — RBAC

```bash
# Получить токен (роли: alice=admin, bob=user, carol=guest)
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice"}'

# Чтение (доступно всем)
curl http://localhost:8000/protected_resource \
  -H "Authorization: Bearer alice-token"

# Создание (только admin)
curl -X POST http://localhost:8000/admin/resource \
  -H "Authorization: Bearer alice-token"

# Удаление от имени user → 403
curl -X DELETE http://localhost:8000/admin/resource \
  -H "Authorization: Bearer bob-token"
```

### Task 8.1 — SQLite: регистрация

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user", "password": "12345"}'
```

### Task 8.2 — SQLite: CRUD Todo

```bash
# Создать
curl -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Купить молоко", "description": "2 пакета"}'

# Получить
curl http://localhost:8000/todos/1

# Обновить
curl -X PUT http://localhost:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Удалить
curl -X DELETE http://localhost:8000/todos/1
```
