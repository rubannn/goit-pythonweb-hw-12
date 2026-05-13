# Contacts API

REST API для керування особистими контактами, побудований на `FastAPI`, `SQLAlchemy`, `PostgreSQL` та `Redis`.

## Можливості

- Реєстрація та логін користувачів
- Хешування паролів і JWT-аутентифікація
- Верифікація email з повторним надсиланням листа
- Скидання пароля через підписані токени з терміном дії
- Ролі користувачів `user` та `admin`
- Кешування поточного користувача в Redis
- Ізоляція контактів за власником
- Пошук контактів і добірка найближчих днів народження
- Обмеження кількості запитів для `GET /api/users/me`
- Завантаження аватара адміністратора через Cloudinary
- Документація Sphinx
- Модульні та інтеграційні тести на `pytest`
- Перевірка покриття через `pytest-cov`
- Запуск через Docker Compose з PostgreSQL, Redis і PgAdmin

## Технології

- `FastAPI`
- `SQLAlchemy 2.0`
- `PostgreSQL`
- `Redis`
- `Pydantic`
- `slowapi`
- `Cloudinary`
- `pytest`
- `Sphinx`

## Структура проєкту

```text
src/
  api/         # Роутери FastAPI
  crud/        # Операції з базою даних
  database/    # Налаштування, сесія БД, seed
  models/      # SQLAlchemy-моделі
  schemas/     # Pydantic-схеми
  services/    # Auth, cache, email, rate limit, Cloudinary
tests/
  unit/        # Модульні тести
  integration/ # Інтеграційні тести
docs/          # Документація Sphinx
```

## Змінні середовища

Створіть `.env` на основі `.env.example`.

Усі конфіденційні значення потрібно зберігати тільки в `.env`, а не в кодовій базі.

```env
APP_NAME=Contacts API
POSTGRES_DB=contacts_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_USER_CACHE_TTL=300

JWT_SECRET_KEY=change-me-super-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

MAIL_USERNAME=example@example.com
MAIL_PASSWORD=app-password
MAIL_FROM=example@example.com
MAIL_PORT=587
MAIL_SERVER=smtp.example.com
MAIL_STARTTLS=true
MAIL_SSL_TLS=false
MAIL_SUPPRESS_SEND=true
EMAIL_VERIFICATION_TOKEN_EXPIRE_SECONDS=3600
PASSWORD_RESET_TOKEN_EXPIRE_SECONDS=3600

BACKEND_BASE_URL=http://localhost:8000
FRONTEND_BASE_URL=http://localhost:3000
PASSWORD_RESET_PAGE_URL=http://localhost:3000/reset-password

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
RATE_LIMIT_ME=5/minute

CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

Примітки:

- `MAIL_SUPPRESS_SEND=true` виводить verification і reset links у логи замість реальної SMTP-відправки.
- `REDIS_USER_CACHE_TTL` визначає час життя кешу поточного користувача.
- Якщо змінні Cloudinary порожні, завантаження аватара поверне `503 Cloudinary is not configured`.

## Запуск через Docker Compose

Основний сценарій:

```bash
make build
```

Ця команда:

- збирає образ `web`
- запускає `web`, `postgres`, `redis` і `pgadmin`
- виконує seed-скрипт

Корисні команди:

```bash
make run
make stop
make restart
make logs
make seed-docker
```

Щоб отримати чисту базу:

```bash
docker compose down -v
make build
```

## Локальний запуск

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload
```

Щоб додати seed-дані локально:

```bash
python -m src.database.seed
```

## Тестування

Локально:

```bash
make test
make test-cov
```

У Docker:

```bash
make test-docker
make test-cov-docker
```

Команда coverage перевіряє поріг не нижче `75%`.

## Документація

Локально:

```bash
make docs
```

У Docker:

```bash
make docs-docker
```

HTML-документація збирається в `docs/_build/html`.

## Доступні сервіси

- API docs: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`
- PgAdmin: `http://127.0.0.1:8080`

Дані входу в PgAdmin:

- email: `admin@example.com`
- password: `admin123`

## Аутентифікація та ролі

### Реєстрація

`POST /api/auth/register`

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "secret123"
}
```

### Верифікація email

`GET /api/auth/verify-email/{token}`

Якщо `MAIL_SUPPRESS_SEND=true`, verification link буде в логах застосунку.

Повторне надсилання листа:

`POST /api/auth/request-email`

### Логін

`POST /api/auth/login`

```json
{
  "email": "test@example.com",
  "password": "secret123"
}
```

### Скидання пароля

Запит на reset link:

`POST /api/auth/request-password-reset`

```json
{
  "email": "test@example.com"
}
```

Підтвердження скидання:

`POST /api/auth/reset-password`

```json
{
  "token": "reset-token",
  "new_password": "newsecret123"
}
```

Якщо `MAIL_SUPPRESS_SEND=true`, reset link також з’явиться в логах.

### Ролі

- Нові користувачі отримують роль `user`
- Лише користувач із роллю `admin` може змінювати свій аватар через `PATCH /api/users/avatar`

## Основні endpoint-и API

### Auth

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/verify-email/{token}`
- `POST /api/auth/request-email`
- `POST /api/auth/request-password-reset`
- `POST /api/auth/reset-password`

### Users

- `GET /api/users/me`
- `PATCH /api/users/avatar`

### Contacts

- `POST /api/contacts/`
- `GET /api/contacts/`
- `GET /api/contacts/{contact_id}`
- `PUT /api/contacts/{contact_id}`
- `DELETE /api/contacts/{contact_id}`
- `GET /api/contacts/upcoming-birthdays`

## Кешування в Redis

Поточний користувач кешується під час аутентифікації. `get_current_user` спочатку перевіряє Redis і звертається до бази лише при `cache miss`. Кеш оновлюється або інвалідується після:

- успішного логіну
- верифікації email
- оновлення аватара
- скидання пароля

Якщо Redis тимчасово недоступний, аутентифікація продовжує працювати через базу даних.

## Seed-дані

Seed-скрипт:

- [src/database/seed.py](/d:/Python/GoIT/goit-pythonweb-hw-12/src/database/seed.py)

Стандартні користувачі:

- user email: `seed.user@example.com`
- user password: `seedpassword123`
- admin email: `seed.admin@example.com`
- admin password: `seedadmin123`

Усі seed-контакти належать звичайному користувачу.

## Нотатки щодо перевірки

Що вже перевірено в коді:

- компіляція `python -m compileall src tests`
- модульні та інтеграційні тести на `pytest`
- Docker-конфігурація через `.env` і `docker-compose.yml`

Що варто перевірити після запуску:

1. Зареєструвати нового користувача.
2. Підтвердити email через verification link.
3. Залогінитися й отримати `access_token`.
4. Викликати `GET /api/users/me`.
5. Виконати сценарій скидання пароля.
6. Створити контакти й перевірити ізоляцію між користувачами.
7. Увійти як адміністратор і завантажити аватар.
