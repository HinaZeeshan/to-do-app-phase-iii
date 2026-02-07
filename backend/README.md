# Todo Backend API

Secure RESTful backend API for multi-user task management with FastAPI, Neon PostgreSQL, and SQLModel.

## Architecture

**Layered Architecture**:
- **Models**: SQLModel definitions (database schema)
- **Schemas**: Pydantic models for API requests/responses
- **Repositories**: Database query logic (async CRUD operations)
- **Services**: Business logic, authorization checks
- **Routers**: FastAPI endpoints, HTTP handling

## Tech Stack

- **Framework**: FastAPI 0.109+
- **Database**: Neon Serverless PostgreSQL 15+
- **ORM**: SQLModel 0.0.14+
- **DB Driver**: asyncpg 0.29+ (async PostgreSQL)
- **JWT**: python-jose 3.3+
- **Server**: Uvicorn 0.27+
- **Testing**: pytest 8.0+ with pytest-asyncio
- **Python**: 3.11+

## Quick Setup

### 1. Install Dependencies

```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install
pip install -e ".[dev]"
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your DATABASE_URL and JWT_SECRET
```

### 3. Run Migrations

```bash
alembic upgrade head
```

### 4. Start Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000/docs for interactive API documentation.

## Project Structure

```
backend/
├── src/
│   ├── main.py              # FastAPI app initialization
│   ├── config.py            # Settings (loads .env)
│   ├── database.py          # Database connection
│   ├── models/              # SQLModel entities
│   ├── schemas/             # Pydantic request/response models
│   ├── repositories/        # Database queries
│   ├── services/            # Business logic
│   ├── routers/             # API endpoints
│   ├── auth/                # JWT verification
│   └── middleware/          # Error handling, request ID
├── tests/
│   ├── contract/            # API contract tests
│   ├── integration/         # End-to-end tests
│   └── unit/                # Unit tests per layer
├── alembic/                 # Database migrations
├── .env                     # Environment variables (not in git)
├── .env.example             # Example template
├── pyproject.toml           # Dependencies
└── README.md                # This file
```

## API Endpoints

All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

### List All Tasks
```http
GET /api/{user_id}/tasks
Authorization: Bearer <token>
```
**Response 200**: `TaskListResponse` with array of tasks and metadata
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Buy groceries",
      "is_completed": false,
      "completed_at": null,
      "created_at": "2026-01-14T10:00:00Z",
      "updated_at": "2026-01-14T10:00:00Z"
    }
  ],
  "meta": {
    "timestamp": "2026-01-14T12:00:00Z",
    "count": 1
  }
}
```

### Create New Task
```http
POST /api/{user_id}/tasks
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Buy groceries"
}
```
**Response 201**: `TaskResponse` with created task details

### Get Single Task
```http
GET /api/{user_id}/tasks/{id}
Authorization: Bearer <token>
```
**Response 200**: `TaskResponse` with task details
**Response 404**: Task not found or doesn't belong to user

### Update Task
```http
PUT /api/{user_id}/tasks/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Buy organic groceries",
  "is_completed": false
}
```
**Response 200**: `TaskResponse` with updated task
**Note**: Both fields are optional (partial update)

### Mark Task Complete
```http
PATCH /api/{user_id}/tasks/{id}/complete
Authorization: Bearer <token>
```
**Response 200**: `TaskResponse` with `is_completed=true` and `completed_at` timestamp
**Note**: Idempotent operation (no error if already complete)

### Delete Task
```http
DELETE /api/{user_id}/tasks/{id}
Authorization: Bearer <token>
```
**Response 204**: No Content on success

## Security

- JWT validation on every request (no exceptions)
- URL `user_id` must match JWT `user_id` claim (403 if mismatch)
- All database queries filter by authenticated `user_id`
- Zero cross-user data access (enforced at app + DB layers)
- Secrets in `.env` (never hardcoded)

## Development

### Authentication Setup

This backend includes JWT-based authentication with the following endpoints:

- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/login` - Authenticate existing user
- `POST /api/auth/logout` - End user session

**Setup**:
1. Configure JWT_SECRET in `.env` (minimum 256-bit random string)
2. Run `alembic upgrade head` to create users and auth_events tables
3. Access authentication endpoints at `http://localhost:8000/api/auth/`

**Security Features**:
- Passwords hashed using bcrypt
- Rate limiting: 5 attempts per minute per IP
- JWT tokens expire after 24 hours
- All authentication events logged for security monitoring

### Run Tests

```bash
pytest tests/ -v
```

### Lint and Format

```bash
ruff check src/
black src/
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Performance Targets

- API p95 latency: <200ms
- Concurrent users: 100+
- Tasks per user: 1000+ without degradation

## Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

See `/specs/001-backend-api/quickstart.md` for detailed setup and testing guide.

## Deployment to Hugging Face Spaces

This backend can be deployed to Hugging Face Spaces using the provided Docker configuration:

### Prerequisites
- Dockerfile and .dockerignore are included in the repository
- Application is configured to run on port 7860 (required by Hugging Face Spaces)
- Working directory is set to `/app` as expected by Hugging Face

### Deployment Steps
1. Create a new Space with Docker environment on Hugging Face Hub
2. Point your Space to this repository
3. The Dockerfile will automatically:
   - Set working directory to `/app`
   - Install Python dependencies from pyproject.toml
   - Copy application code
   - Expose port 7860
   - Run the application with uvicorn on `--host 0.0.0.0 --port 7860`

### Environment Variables
Configure these secrets in your Hugging Face Space settings:
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET`: Secret key for JWT token signing
- `CORS_ORIGINS`: Comma-separated list of allowed origins
