# Quickstart Guide: Backend API & Database

**Feature**: Backend API & Database
**Branch**: 001-backend-api
**Date**: 2026-01-14
**Purpose**: Developer onboarding and local testing guide

## Prerequisites

- Python 3.11+ installed
- PostgreSQL access (Neon Serverless recommended)
- Git
- Code editor (VS Code recommended)
- API testing tool (curl, HTTPie, or Postman)

## Quick Setup (5 minutes)

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd <repository-name>
git checkout 001-backend-api
cd backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -e ".[dev]"
```

This installs:
- FastAPI (web framework)
- SQLModel (ORM)
- asyncpg (PostgreSQL driver)
- python-jose (JWT handling)
- uvicorn (ASGI server)
- pytest (testing)

### 4. Configure Environment

Create `.env` file in `backend/` directory:

```bash
cp .env.example .env
```

Edit `.env`:

```ini
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
# Example for Neon: postgresql+asyncpg://user:password@ep-xxx.region.aws.neon.tech/dbname

# Security
JWT_SECRET=your-super-secret-key-min-32-chars-please-change-in-production
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 5. Run Database Migrations

```bash
# Install Alembic if not already installed
pip install alembic

# Initialize migrations (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Create tasks table"

# Apply migrations
alembic upgrade head
```

### 6. Start Development Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [PID] using WatchFiles
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 7. Verify Installation

Open browser to http://localhost:8000/docs

You should see the auto-generated FastAPI Swagger UI with all 6 endpoints.

---

## Testing the API

### Get JWT Token (Placeholder)

**Note**: Authentication system is Spec-2. For local testing, generate a test JWT:

```python
# test_jwt.py
from jose import jwt
from datetime import datetime, timedelta
import os

payload = {
    "user_id": "123e4567-e89b-12d3-a456-426614174000",  # Test user UUID
    "exp": datetime.utcnow() + timedelta(hours=24)
}

token = jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm="HS256")
print(f"Bearer {token}")
```

Run:
```bash
python test_jwt.py
```

Copy the output token.

### Test Endpoints with curl

Export your token for convenience:
```bash
export TOKEN="<paste-token-here>"
export USER_ID="123e4567-e89b-12d3-a456-426614174000"
```

#### 1. Create a Task

```bash
curl -X POST "http://localhost:8000/api/$USER_ID/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries"}'
```

Expected response (201 Created):
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Buy groceries",
    "is_completed": false,
    "completed_at": null,
    "created_at": "2026-01-14T10:00:00Z",
    "updated_at": "2026-01-14T10:00:00Z"
  },
  "meta": {
    "timestamp": "2026-01-14T10:00:00Z",
    "request_id": "..."
  }
}
```

#### 2. List All Tasks

```bash
curl -X GET "http://localhost:8000/api/$USER_ID/tasks" \
  -H "Authorization: Bearer $TOKEN"
```

#### 3. Get Single Task

```bash
export TASK_ID="<paste-task-id-from-create-response>"
curl -X GET "http://localhost:8000/api/$USER_ID/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN"
```

#### 4. Update Task

```bash
curl -X PUT "http://localhost:8000/api/$USER_ID/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy organic groceries"}'
```

#### 5. Mark Task Complete

```bash
curl -X PATCH "http://localhost:8000/api/$USER_ID/tasks/$TASK_ID/complete" \
  -H "Authorization: Bearer $TOKEN"
```

#### 6. Delete Task

```bash
curl -X DELETE "http://localhost:8000/api/$USER_ID/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN"
```

Expected response: 204 No Content

---

## Testing User Isolation

### Test Cross-User Access Protection

Create a second user's JWT:
```python
payload = {
    "user_id": "987e6543-e21c-98d7-a654-321456987000",  # Different user
    "exp": datetime.utcnow() + timedelta(hours=24)
}
token2 = jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm="HS256")
```

Try accessing User A's tasks with User B's token:
```bash
export TOKEN2="<user-b-token>"
curl -X GET "http://localhost:8000/api/$USER_ID/tasks" \
  -H "Authorization: Bearer $TOKEN2"
```

Expected response (403 Forbidden):
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "Access denied - user_id mismatch",
    "details": null,
    "timestamp": "2026-01-14T10:00:00Z",
    "request_id": "..."
  }
}
```

---

## Running Tests

### Unit Tests

```bash
pytest backend/tests/unit -v
```

### Integration Tests

```bash
# Requires test database
export DATABASE_URL=postgresql+asyncpg://user:password@host:5432/test_db
pytest backend/tests/integration -v
```

### Contract Tests

```bash
pytest backend/tests/contract -v
```

### All Tests with Coverage

```bash
pytest backend/tests --cov=backend/src --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

---

## Project Structure

```
backend/
├── src/
│   ├── main.py              # FastAPI app initialization
│   ├── config.py            # Settings (loads .env)
│   ├── database.py          # Database connection and session
│   ├── models/
│   │   └── task.py          # SQLModel Task model
│   ├── schemas/
│   │   ├── task.py          # Request/response schemas
│   │   └── error.py         # Error response schemas
│   ├── repositories/
│   │   └── task_repository.py  # Database queries
│   ├── services/
│   │   └── task_service.py  # Business logic
│   ├── routers/
│   │   └── tasks.py         # API endpoints
│   ├── auth/
│   │   └── dependencies.py  # JWT verification
│   └── middleware/
│       ├── error_handler.py # Global exception handling
│       └── request_id.py    # Request ID middleware
├── tests/
│   ├── contract/            # API contract tests
│   ├── integration/         # End-to-end tests
│   └── unit/                # Unit tests per layer
├── alembic/                 # Database migrations
├── .env                     # Environment variables (not in git)
├── .env.example             # Example environment template
├── pyproject.toml           # Dependencies
└── README.md                # Backend documentation
```

---

## Common Issues & Solutions

### Issue: Database connection fails

**Symptom**: `asyncpg.exceptions.InvalidCatalogNameError`

**Solution**:
1. Verify DATABASE_URL in `.env`
2. Check database exists: `psql -U user -d dbname`
3. For Neon, ensure serverless database is awake (first connection may be slow)

### Issue: JWT validation fails

**Symptom**: `401 Unauthorized - Invalid or expired token`

**Solution**:
1. Verify JWT_SECRET in `.env` matches token generation secret
2. Check token expiration (`exp` claim in JWT payload)
3. Ensure token format: `Bearer <token>` (not just `<token>`)

### Issue: CORS errors in frontend

**Symptom**: `Access to fetch at ... from origin ... has been blocked by CORS policy`

**Solution**:
1. Add frontend origin to CORS_ORIGINS in `.env`
2. Restart FastAPI server after env change
3. Format: `http://localhost:3000` (no trailing slash)

### Issue: Migrations fail

**Symptom**: `alembic.util.exc.CommandError: Can't locate revision identified by ...`

**Solution**:
1. Drop database and recreate: `dropdb dbname && createdb dbname`
2. Delete alembic/versions/*.py
3. Regenerate: `alembic revision --autogenerate -m "Initial"`
4. Apply: `alembic upgrade head`

---

## Development Workflow

### 1. Make Changes

Edit code in `backend/src/`

### 2. Auto-reload Observes Changes

Uvicorn `--reload` flag watches for file changes and restarts automatically.

### 3. Test Changes

```bash
# Quick test specific endpoint
pytest backend/tests/unit/test_tasks.py::test_create_task -v

# Full test suite
pytest backend/tests -v
```

### 4. Check Code Quality

```bash
# Lint
ruff check backend/src

# Format
black backend/src

# Type check (if mypy installed)
mypy backend/src
```

### 5. Commit Changes

```bash
git add backend/src/...
git commit -m "feat: add task completion timestamp"
```

---

## API Documentation

### Auto-generated Swagger UI

http://localhost:8000/docs

Interactive documentation where you can:
- View all endpoints
- See request/response schemas
- Try out endpoints with "Try it out" button
- Authorize with JWT token (click "Authorize" button, enter `Bearer <token>`)

### ReDoc (Alternative UI)

http://localhost:8000/redoc

Alternative documentation view (read-only, better for printing).

### OpenAPI JSON

http://localhost:8000/openapi.json

Raw OpenAPI specification (useful for code generation tools).

---

## Performance Testing

### Simple Load Test with Apache Bench

```bash
# Install Apache Bench
# macOS: brew install httpie
# Ubuntu: apt-get install apache2-utils

# Test list endpoint (100 requests, 10 concurrent)
ab -n 100 -c 10 \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/$USER_ID/tasks
```

Expected results (on local dev machine):
- Requests per second: >500
- Mean response time: <20ms
- P95 response time: <50ms

### Profile with Locust (Advanced)

```bash
# Install
pip install locust

# Create locustfile.py
locust -f backend/tests/performance/locustfile.py
```

Access web UI at http://localhost:8089

---

## Debugging Tips

### Enable SQL Logging

Edit `backend/src/database.py`:
```python
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # <-- Change to True
    ...
)
```

Now all SQL queries will be printed to console.

### Add Request Logging Middleware

Edit `backend/src/main.py`:
```python
import logging

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logging.info(f"Status: {response.status_code}")
    return response
```

### Use Python Debugger

Add breakpoint in code:
```python
import pdb; pdb.set_trace()
```

Or use VS Code debugger:
1. Set breakpoint in editor (click left of line number)
2. Run > Start Debugging (F5)
3. Select "FastAPI" configuration

---

## Next Steps

1. **Integrate with authentication system** (Spec-2) - Replace test JWT with real Better Auth tokens
2. **Add frontend** (Spec-3) - Build Next.js UI that calls these endpoints
3. **Deploy to production** - Configure production DATABASE_URL and JWT_SECRET
4. **Add monitoring** - Set up logging, metrics, and error tracking
5. **Optimize performance** - Add caching, database query optimization

---

## Support

- **API Issues**: Check FastAPI logs (uvicorn console output)
- **Database Issues**: Check PostgreSQL logs
- **JWT Issues**: Validate token at https://jwt.io
- **General Questions**: See README.md or ask team

---

## Checklist: Ready to Develop?

- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] `.env` file configured with valid DATABASE_URL and JWT_SECRET
- [ ] Database migrations applied successfully
- [ ] Development server starts without errors
- [ ] Swagger UI accessible at http://localhost:8000/docs
- [ ] Test JWT token generated
- [ ] Successfully created and retrieved a task
- [ ] Tests pass: `pytest backend/tests`

If all checked, you're ready to implement the feature! 🚀
