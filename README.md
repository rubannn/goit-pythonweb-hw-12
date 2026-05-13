# Contacts API

REST API for managing personal contacts built with `FastAPI`, `SQLAlchemy`, `PostgreSQL`, and `Redis`.

## Features

- User registration and login
- Password hashing with JWT authentication
- Email verification with resend flow
- Password reset flow with signed expiring tokens
- Role-based access with `user` and `admin`
- Redis caching for `get_current_user`
- Contact isolation by owner
- Contact search and upcoming birthdays
- Rate limiting for `GET /api/users/me`
- Admin-only avatar upload through Cloudinary
- Sphinx documentation
- Unit and integration tests with `pytest`
- Coverage check with `pytest-cov`
- Docker Compose setup with PostgreSQL, Redis, and PgAdmin

## Tech Stack

- `FastAPI`
- `SQLAlchemy 2.0`
- `PostgreSQL`
- `Redis`
- `Pydantic`
- `slowapi`
- `Cloudinary`
- `pytest`
- `Sphinx`

## Project Structure

```text
src/
  api/         # FastAPI routers
  crud/        # Database operations
  database/    # Settings, DB session, seed
  models/      # SQLAlchemy models
  schemas/     # Pydantic schemas
  services/    # Auth, cache, email, rate limit, Cloudinary
tests/
  unit/        # Unit tests
  integration/ # Integration tests
docs/          # Sphinx documentation
```

## Environment Variables

Create `.env` from `.env.example`.

All sensitive settings must stay in `.env` and must not be hardcoded in the repository.

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

Notes:

- `MAIL_SUPPRESS_SEND=true` prints verification and reset links to logs instead of sending SMTP email.
- `REDIS_USER_CACHE_TTL` controls how long the cached current user stays in Redis.
- If Cloudinary variables are empty, avatar upload returns `503 Cloudinary is not configured`.

## Run with Docker Compose

Main flow:

```bash
make build
```

This command:

- builds the `web` image
- starts `web`, `postgres`, `redis`, and `pgadmin`
- runs the seed script

Useful commands:

```bash
make run
make stop
make restart
make logs
make seed-docker
```

If you need a fresh database:

```bash
docker compose down -v
make build
```

## Run Locally

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload
```

Seed data locally:

```bash
python -m src.database.seed
```

## Testing

Local:

```bash
make test
make test-cov
```

Docker:

```bash
make test-docker
make test-cov-docker
```

The coverage command enforces a minimum threshold of `75%`.

## Documentation

Local:

```bash
make docs
```

Docker:

```bash
make docs-docker
```

Generated HTML is written to `docs/_build/html`.

## Available Services

- API docs: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`
- PgAdmin: `http://127.0.0.1:8080`

PgAdmin credentials:

- email: `admin@example.com`
- password: `admin123`

## Authentication and Roles

### Register

`POST /api/auth/register`

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "secret123"
}
```

### Verify Email

`GET /api/auth/verify-email/{token}`

If `MAIL_SUPPRESS_SEND=true`, copy the verification link from application logs.

Resend verification:

`POST /api/auth/request-email`

### Login

`POST /api/auth/login`

```json
{
  "email": "test@example.com",
  "password": "secret123"
}
```

### Password Reset

Request reset link:

`POST /api/auth/request-password-reset`

```json
{
  "email": "test@example.com"
}
```

Confirm reset:

`POST /api/auth/reset-password`

```json
{
  "token": "reset-token",
  "new_password": "newsecret123"
}
```

If `MAIL_SUPPRESS_SEND=true`, the reset link is printed to logs.

### Roles

- New users are created with role `user`
- Only users with role `admin` can update their avatar through `PATCH /api/users/avatar`

## Main API Endpoints

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

## Redis Caching

The current user is cached in Redis during authentication flow. `get_current_user` first checks Redis and only hits the database on cache miss. Cache is refreshed or invalidated after:

- successful login
- email verification
- avatar update
- password reset

If Redis is unavailable, authentication falls back to the database.

## Seed Data

Seed script:

- [src/database/seed.py](/d:/Python/GoIT/goit-pythonweb-hw-12/src/database/seed.py)

Default seeded users:

- user email: `seed.user@example.com`
- user password: `seedpassword123`
- admin email: `seed.admin@example.com`
- admin password: `seedadmin123`

Seeded contacts belong to the seeded regular user.

## Verification Notes

What was verified in code:

- syntax compilation with `python -m compileall src tests`
- unit and integration tests with `pytest`
- Docker-oriented configuration via `.env` and `docker-compose.yml`

Recommended final checks after startup:

1. Register a new user.
2. Confirm email through the verification link.
3. Login and get `access_token`.
4. Call `GET /api/users/me`.
5. Request and complete a password reset.
6. Create contacts and confirm isolation between users.
7. Login as admin and upload an avatar.
