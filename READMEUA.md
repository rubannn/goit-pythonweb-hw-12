# Contacts API

REST API для керування особистими контактами, побудований на `FastAPI`, `SQLAlchemy` та `PostgreSQL`.

## Можливості

- Реєстрація та логін користувачів
- Хешування паролів
- JWT-аутентифікація через `access_token`
- Доступ до контактів лише для автентифікованих користувачів
- Ізоляція контактів за власником
- Верифікація email з повторною відправкою листа
- Обмеження кількості запитів для `GET /api/users/me`
- Налаштування CORS через `.env`
- Завантаження аватара користувача через Cloudinary
- Swagger-документація
- Запуск через Docker Compose з PostgreSQL та PgAdmin

## Технології

- `FastAPI`
- `SQLAlchemy 2.0`
- `PostgreSQL`
- `Pydantic`
- `slowapi`
- `Cloudinary`

## Структура проєкту

```text
src/
  api/         # Роутери FastAPI
  crud/        # Операції з базою даних
  database/    # Налаштування, сесія БД, seed
  models/      # SQLAlchemy-моделі
  schemas/     # Pydantic-схеми
  services/    # Auth, email, rate limit, Cloudinary
```

## Змінні середовища

Створіть `.env` на основі `.env.example`.

Основні змінні:

```env
APP_NAME=Contacts API
POSTGRES_DB=contacts_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

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
BACKEND_BASE_URL=http://localhost:8000
FRONTEND_BASE_URL=http://localhost:3000

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
RATE_LIMIT_ME=5/minute

CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

Примітки:

- `MAIL_SUPPRESS_SEND=true` зручно для локальної розробки. У цьому режимі посилання верифікації не відправляється SMTP, а виводиться в логи застосунку.
- `RATE_LIMIT_ME` приймає значення на кшталт `5/minute`, `10/minute`, `2/second`.
- Якщо змінні Cloudinary порожні, завантаження аватара поверне `503 Cloudinary is not configured`.

## Запуск через Docker Compose

Основний сценарій:

```bash
make build
```

Ця команда:

- збирає образ `web`
- запускає `web`, `postgres` і `pgadmin`
- виконує seed-скрипт

Корисні команди:

```bash
make run
make stop
make restart
make logs
make seed-docker
```

Якщо раніше використовувалась стара схема БД, перед фінальною перевіркою краще пересоздати volume:

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

## Доступні сервіси

- API docs: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`
- PgAdmin: `http://127.0.0.1:8080`

Дані входу в PgAdmin:

- email: `admin@example.com`
- password: `admin123`

## Сценарій автентифікації

### 1. Реєстрація

`POST /api/auth/register`

Приклад тіла запиту:

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "secret123"
}
```

Поведінка:

- повертає `201 Created` при успішній реєстрації
- повертає `409 Conflict`, якщо email уже існує
- зберігає пароль у вигляді хешу

### 2. Верифікація email

Якщо `MAIL_SUPPRESS_SEND=true`, після реєстрації відкрийте логи застосунку й скопіюйте verification link.

Також можна повторно запросити лист:

`POST /api/auth/request-email`

```json
{
  "email": "test@example.com"
}
```

### 3. Логін

`POST /api/auth/login`

```json
{
  "email": "test@example.com",
  "password": "secret123"
}
```

Відповідь:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

### 4. Авторизація в Swagger

- відкрийте `/docs`
- натисніть `Authorize`
- вставте тільки `access_token`

## Основні endpoint-и API

### Auth

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/verify-email/{token}`
- `POST /api/auth/request-email`

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
- `GET /api/contacts/?first_name=...`
- `GET /api/contacts/?last_name=...`
- `GET /api/contacts/?email=...`

## Завантаження аватара

Використовуйте `PATCH /api/users/avatar` з multipart form-data полем `file`.

Приклад з `curl`:

```bash
curl -X PATCH "http://127.0.0.1:8000/api/users/avatar" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/avatar.jpg"
```

Також це можна перевірити через Swagger UI.

## Seed-дані

Seed-скрипт:

- [src/database/seed.py](D:\Python\GoIT\goit-pythonweb-hw-10\src\database\seed.py)

Стандартний seed-користувач:

- email: `seed.user@example.com`
- password: `seedpassword123`

Усі seed-контакти належать саме цьому користувачу.

## Що перевірити після запуску

1. Зареєструвати нового користувача.
2. Підтвердити email через verification link.
3. Залогінитися й отримати `access_token`.
4. Викликати `GET /api/users/me`.
5. Створити контакти й перевірити ізоляцію між користувачами.
6. Завантажити аватар і переконатися, що повертається `avatar_url`.
