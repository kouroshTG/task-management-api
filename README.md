# Task Management API

A RESTful Task Management API built with **Python, FastAPI, PostgreSQL, and SQLAlchemy**.

This project provides user authentication, task management, ownership-based access control, filtering, search, and pagination. It is designed with a layered architecture to keep API endpoints, business logic, and database operations separated.

## Features

### Authentication & Users
- User registration and login
- JWT-based authentication
- Secure password hashing using Argon2
- Retrieve the authenticated user's profile
- Protected endpoints

### Task Management
- Create, retrieve, update, and delete tasks
- Ownership-based authorization
- Task status management:
  - `pending`
  - `in_progress`
  - `completed`
- Task priority levels:
  - `low`
  - `medium`
  - `high`
- Optional task descriptions and due dates
- Partial updates using HTTP PATCH

### Filtering & Pagination
- Filter tasks by status
- Filter tasks by priority
- Search task titles and descriptions
- Case-insensitive search using PostgreSQL ILIKE
- Pagination using `limit` and `offset`
- Newest tasks returned first

### Database & Deployment
- PostgreSQL database
- SQLAlchemy 2.x ORM
- Database migrations with Alembic
- Docker and Docker Compose
- PostgreSQL health checks

### Testing & Code Quality
- Automated tests with Pytest
- HTTP endpoint testing
- Code quality checks with Ruff

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Programming language |
| FastAPI | REST API framework |
| PostgreSQL 16 | Relational database |
| SQLAlchemy 2.x | ORM |
| Alembic | Database migrations |
| Pydantic v2 | Data validation |
| PyJWT | JWT authentication |
| pwdlib / Argon2 | Password hashing |
| Pytest | Automated testing |
| Ruff | Linting |
| Docker Compose | Container orchestration |

## Architecture

The application follows a layered architecture:

```text
app/
├── api/
│   ├── dependencies.py
│   └── v1/
│       ├── endpoints/
│       │   ├── auth.py
│       │   ├── health.py
│       │   ├── tasks.py
│       │   └── users.py
│       └── router.py
├── core/
│   ├── config.py
│   └── security.py
├── db/
│   ├── base.py
│   └── session.py
├── models/
├── repositories/
├── schemas/
└── services/

migrations/
tests/
```

**Layer responsibilities:**

- **API:** Handles HTTP requests, responses, and dependency injection.
- **Schemas:** Validates incoming data and structures API responses.
- **Services:** Implements application business logic and transaction handling.
- **Repositories:** Encapsulates database queries and persistence operations.
- **Models:** Defines SQLAlchemy database models.
- **Core:** Contains application configuration and security utilities.
- **DB:** Manages database connections and session setup.
- **Migrations:** Contains Alembic database migration scripts.
- **Tests:** Contains automated tests.

## Getting Started

### Prerequisites

- Python 3.12
- PostgreSQL 16
- Git

For Docker-based setup:

- Docker Engine
- Docker Compose

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd task-management-api
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and configure your database credentials and secret key.

Generate a secure secret key:

```bash
openssl rand -hex 32
```

Use a strong database password and keep `.env` out of version control.

### 3. Run with Docker Compose

```bash
docker compose up -d --build
```

Check container status:

```bash
docker compose ps
```

View API logs:

```bash
docker compose logs -f api
```

The API will be available at:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

### 4. Run locally without Docker

Create and activate a virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -e ".[dev]"
```

Configure `.env` with a PostgreSQL connection URL pointing to your local database.

Run migrations:

```bash
alembic upgrade head
```

Start the development server:

```bash
uvicorn app.main:app --reload
```

## API Reference

All application endpoints use the `/api/v1` prefix.

### Health

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| GET | `/health` | Check API health | No |

### Authentication

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/login` | Authenticate and receive an access token | No |

### Users

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| GET | `/users/me` | Retrieve current user profile | Yes |

### Tasks

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| POST | `/tasks/` | Create a task | Yes |
| GET | `/tasks/` | List and filter tasks | Yes |
| GET | `/tasks/{task_id}` | Retrieve a task | Yes |
| PATCH | `/tasks/{task_id}` | Partially update a task | Yes |
| DELETE | `/tasks/{task_id}` | Delete a task | Yes |

### Authentication Flow

1. Register using `POST /api/v1/auth/register`.
2. Log in using `POST /api/v1/auth/login`.
3. Copy the returned `access_token`.
4. Include the token in protected requests:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Example Requests

### Register

```http
POST /api/v1/auth/register
Content-Type: application/json
```

```json
{
  "email": "user@example.com",
  "password": "strong-password",
  "full_name": "Example User"
}
```

### Login

```http
POST /api/v1/auth/login
Content-Type: application/json
```

```json
{
  "email": "user@example.com",
  "password": "strong-password"
}
```

### Create a Task

```http
POST /api/v1/tasks/
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

```json
{
  "title": "Complete backend project",
  "description": "Finish API documentation and tests",
  "priority": "high",
  "due_date": "2026-12-01T18:00:00Z"
}
```

### Filter and Search Tasks

```http
GET /api/v1/tasks/?status=pending&priority=high&search=backend&limit=10&offset=0
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Available query parameters:

| Parameter | Description | Default |
|---|---|---|
| `status` | Filter by task status | None |
| `priority` | Filter by priority | None |
| `search` | Search title and description | None |
| `limit` | Number of results (1–100) | 20 |
| `offset` | Number of records to skip | 0 |

### Update a Task

```http
PATCH /api/v1/tasks/1
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

```json
{
  "status": "in_progress",
  "priority": "high"
}
```

### Delete a Task

```http
DELETE /api/v1/tasks/1
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Testing

Run the complete test suite:

```bash
pytest -q
```

Run linting:

```bash
ruff check app tests
```

## Security Considerations

- Passwords are stored as Argon2 hashes, not plaintext.
- Protected endpoints require JWT authentication.
- Task operations are restricted to their owners.
- Task creation does not allow clients to assign an arbitrary owner ID.
- Environment secrets are excluded from version control.
- Request data is validated using Pydantic.

## Future Improvements

Potential areas for further development:

- Refresh token support
- Role-based access control
- Task labels and categories
- Rate limiting
- Structured logging
- CI/CD with GitHub Actions
- API integration tests in CI
- Production deployment configuration

## License

This project is currently available for portfolio and educational purposes. A formal license can be added before public distribution.
