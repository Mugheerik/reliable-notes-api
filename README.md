# Reliable Notes API

A production-minded REST API for managing personal notes, built with **FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT authentication, Docker, and pytest**.

The project focuses on building a reliable backend service with authentication, authorization, database migrations, validation, automated testing, and containerized development.

## Features

* User registration and login
* Secure password hashing with Argon2
* JWT-based authentication
* Authenticated user profile endpoint
* Create, read, update, and delete notes
* Archive and unarchive notes
* Search notes by title or content
* Pagination with limit and offset
* User ownership and access isolation
* Request and response validation with Pydantic
* PostgreSQL persistence
* Database migrations with Alembic
* Automated API tests with pytest
* Dockerized FastAPI application
* Docker Compose development environment
* CI workflow with GitHub Actions

## Tech Stack

| Area               | Technology                 |
| ------------------ | -------------------------- |
| Language           | Python 3.13                |
| API                | FastAPI                    |
| Validation         | Pydantic                   |
| Database           | PostgreSQL 17              |
| ORM                | SQLAlchemy                 |
| Migrations         | Alembic                    |
| Authentication     | JWT                        |
| Password hashing   | Argon2 via pwdlib          |
| Testing            | pytest, FastAPI TestClient |
| Package management | uv                         |
| Containers         | Docker, Docker Compose     |
| CI                 | GitHub Actions             |

## API

### Authentication

```text
POST /auth/register
POST /auth/login
```

### Users

```text
GET /users/me
```

### Notes

```text
POST   /notes
GET    /notes
GET    /notes/{note_id}
PATCH  /notes/{note_id}
DELETE /notes/{note_id}

POST /notes/{note_id}/archive
POST /notes/{note_id}/unarchive
```

The notes listing endpoint supports:

```text
GET /notes?search=python&archived=false&limit=20&offset=0
```

## Architecture

The application currently uses a simple modular backend structure rather than introducing unnecessary architectural complexity.

```text
Client
  │
  ▼
FastAPI
  │
  ├── Authentication / Authorization
  │
  ├── Pydantic validation
  │
  └── SQLAlchemy
          │
          ▼
      PostgreSQL
```

The application and database run as separate Docker Compose services:

```text
┌──────────────────────┐
│   FastAPI Container  │
│                      │
│   Python + FastAPI   │
└──────────┬───────────┘
           │
           │ PostgreSQL
           ▼
┌──────────────────────┐
│ PostgreSQL Container │
└──────────────────────┘
```

Database schema changes are managed through **Alembic migrations** rather than creating tables automatically at application startup.

## Project Structure

```text
reliable-notes-api/
├── .github/
│   └── workflows/
│       └── ci.yml
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── src/
│   └── reliable_notes_api/
│       ├── __init__.py
│       ├── auth.py
│       ├── database.py
│       ├── main.py
│       ├── models.py
│       ├── schemas.py
│       └── security.py
├── tests/
│   ├── conftest.py
│   └── test_api.py
├── .dockerignore
├── .env
├── .gitignore
├── alembic.ini
├── compose.yaml
├── Dockerfile
├── pyproject.toml
├── README.md
└── uv.lock
```

## Running Locally

### Prerequisites

Make sure you have:

* Python 3.13
* uv
* Docker Desktop
* Git

### 1. Clone the repository

```bash
git clone git@github.com:Mugheerik/reliable-notes-api.git
cd reliable-notes-api
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/reliable_notes
TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/reliable_notes_test

JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Do not commit `.env` or real secrets to version control.

### 3. Start PostgreSQL

```bash
docker compose up -d db
```

### 4. Install dependencies

```bash
uv sync
```

### 5. Apply database migrations

```bash
uv run alembic upgrade head
```

### 6. Start the API

```bash
uv run fastapi dev src/reliable_notes_api/main.py
```

The API will be available at:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

## Running with Docker

Build the application image:

```bash
docker compose build
```

Start the application and database:

```bash
docker compose up -d
```

Apply migrations:

```bash
docker compose exec app alembic upgrade head
```

Check running services:

```bash
docker compose ps
```

The API will then be available at:

```text
http://localhost:8000
```

## Testing

The test suite uses a dedicated PostgreSQL database so tests run against the same database technology used by the application.

Run the tests locally with:

```bash
uv run pytest
```

The project currently contains **26 API tests** covering:

* Authentication
* Validation
* User registration
* Login failures
* Protected endpoints
* Note CRUD operations
* Archiving
* Searching
* Pagination
* Ownership isolation
* Error handling

## CI

GitHub Actions runs the test suite automatically on:

* Pushes to `main`
* Pull requests targeting `main`

The CI environment creates a temporary PostgreSQL 17 service and runs the project's tests against it.

```text
GitHub
   │
   ▼
GitHub Actions
   │
   ├── Python 3.13
   ├── uv
   ├── PostgreSQL 17
   │
   └── pytest
```

## Engineering Practices Demonstrated

This project is intentionally small, but it demonstrates several practices used in real backend development:

* REST API design
* Authentication and authorization
* Password security
* Input validation
* Database modeling
* Foreign-key relationships
* Database migrations
* Automated testing
* Test database isolation
* Docker containerization
* Environment-based configuration
* CI automation
* Ownership-based authorization
* Clean Git workflow

The project prioritizes **simple, maintainable engineering over unnecessary architectural complexity**.

## Project Status

**Current status: Complete — Backend Foundation**

The project establishes the backend foundation for the next stage of the engineering roadmap, where additional concerns such as caching, rate limiting, performance, and production operation can be introduced when they are actually required.

## License

This project is available for educational and portfolio purposes.
