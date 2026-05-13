# Contacts API

REST API for managing personal contacts built with `FastAPI`, `SQLAlchemy`, and `PostgreSQL`.

## Features

- User registration and login
- Password hashing
- JWT authentication with `access_token`
- Access to contacts only for authenticated users
- Contact isolation by owner
- Email verification with resend flow
- Rate limiting for `GET /api/users/me`
- CORS configuration from `.env`
- User avatar upload via Cloudinary
- Swagger documentation
- Docker Compose setup with PostgreSQL and PgAdmin

## Tech Stack

- `FastAPI`
- `SQLAlchemy 2.0`
- `PostgreSQL`
- `Pydantic`
- `slowapi`
- `Cloudinary`

## Project Structure

```text
src/
  api/         # FastAPI routers
  crud/        # Database operations
  database/    # Settings, DB session, seed
  models/      # SQLAlchemy models
  schemas/     # Pydantic schemas
  services/    # Auth, email, rate limit, Cloudinary
```

## Environment Variables

Create `.env` from `.env.example`.

Required core variables:

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

Notes:

- `MAIL_SUPPRESS_SEND=true` is convenient for local development. In this mode the verification link is printed to application logs instead of being sent by SMTP.
- `RATE_LIMIT_ME` accepts values like `5/minute`, `10/minute`, `2/second`.
- If Cloudinary variables are empty, avatar upload returns `503 Cloudinary is not configured`.

## Run with Docker Compose

Main flow:

```bash
make build
```

This command:

- builds the `web` image
- starts `web`, `postgres`, and `pgadmin`
- runs the seed script

Useful commands:

```bash
make run
make stop
make restart
make logs
make seed-docker
```

If you previously ran an older database schema, recreate volumes before testing the final version:

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

## Available Services

- API docs: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`
- PgAdmin: `http://127.0.0.1:8080`

PgAdmin credentials:

- email: `admin@example.com`
- password: `admin123`

## Authentication Flow

### 1. Register

`POST /api/auth/register`

Example body:

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "secret123"
}
```

Behavior:

- returns `201 Created` on success
- returns `409 Conflict` if email already exists
- stores password as hash

### 2. Verify Email

If `MAIL_SUPPRESS_SEND=true`, open application logs and copy the verification link printed after registration.

You can also request another verification email:

`POST /api/auth/request-email`

```json
{
  "email": "test@example.com"
}
```

### 3. Login

`POST /api/auth/login`

```json
{
  "email": "test@example.com",
  "password": "secret123"
}
```

Response:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

### 4. Authorize in Swagger

- open `/docs`
- click `Authorize`
- paste only the `access_token`

## Main API Endpoints

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

## Avatar Upload

Use `PATCH /api/users/avatar` with multipart form-data field `file`.

Example with `curl`:

```bash
curl -X PATCH "http://127.0.0.1:8000/api/users/avatar" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/avatar.jpg"
```

You can also test it from Swagger UI.

## Seed Data

Seed script:

- [src/database/seed.py](D:\Python\GoIT\goit-pythonweb-hw-10\src\database\seed.py)

Default seeded user:

- email: `seed.user@example.com`
- password: `seedpassword123`

Seeded contacts belong to the seeded user.

## Verification Notes

What was verified in code:

- syntax compilation with `python -m compileall src`
- Docker-oriented configuration via `.env` and `docker-compose.yml`

What to verify after startup:

1. Register a new user.
2. Confirm email through verification link.
3. Login and get `access_token`.
4. Call `GET /api/users/me`.
5. Create contacts and confirm isolation between users.
6. Upload avatar and confirm `avatar_url` is returned.
