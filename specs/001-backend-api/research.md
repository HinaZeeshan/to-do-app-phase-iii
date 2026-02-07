# Research: Backend API & Database

**Feature**: Backend API & Database
**Branch**: 001-backend-api
**Date**: 2026-01-14
**Purpose**: Technical research and decision justification for implementation planning

## Research Questions

### Q1: How should we structure the FastAPI project for a web application backend?

**Decision**: Use web application structure with `backend/` directory at repository root

**Rationale**:
- This feature is explicitly backend-only (frontend is Spec-3)
- Separation allows independent deployment and scaling
- Clear boundaries match Constitution Principle III (Separation of Concerns)
- Enables parallel development of frontend and backend teams

**Alternatives Considered**:
1. **Single project structure** (`src/` at root)
   - Rejected: Would mix backend and frontend code when frontend is added
   - Rejected: Doesn't scale well for multi-service architecture
2. **Monorepo with packages** (`packages/backend/`, `packages/frontend/`)
   - Rejected: Over-engineered for this scope
   - May be considered later if additional services are needed

**Implementation Impact**: All backend code lives under `backend/src/`, tests under `backend/tests/`

---

### Q2: What Python version and FastAPI setup should we use?

**Decision**: Python 3.11+ with FastAPI 0.109+, SQLModel 0.0.14+, asyncpg driver

**Rationale**:
- Python 3.11+ provides significant performance improvements (10-60% faster than 3.10)
- FastAPI 0.109+ includes latest async support and Pydantic v2 integration
- SQLModel 0.0.14+ required for PostgreSQL compatibility and type safety
- asyncpg provides best async PostgreSQL performance for FastAPI

**Alternatives Considered**:
1. **Python 3.10**
   - Rejected: Python 3.11 performance gains are significant for API workloads
2. **psycopg2 driver**
   - Rejected: Not async-compatible; would block event loop
3. **Raw SQLAlchemy without SQLModel**
   - Rejected: SQLModel provides Pydantic integration for better type safety

**Implementation Impact**:
- `pyproject.toml` requires Python >=3.11
- Dependencies: `fastapi`, `sqlmodel`, `asyncpg`, `python-jose[cryptography]` (JWT), `python-multipart`, `uvicorn[standard]`

---

### Q3: How should we handle JWT validation middleware?

**Decision**: Implement custom FastAPI dependency using `python-jose` for JWT verification

**Rationale**:
- FastAPI's dependency injection system is ideal for authentication
- `python-jose` is industry-standard for JWT handling in Python
- Dependency approach makes auth testable and reusable across endpoints
- Matches Constitution Security Requirements (JWT validation on every request)

**Implementation**:
```python
# backend/src/auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import JWTError, jwt
import os

security = HTTPBearer()

async def verify_jwt(credentials: HTTPAuthCredentials = Depends(security)) -> dict:
    """
    Verify JWT token and return claims.
    Raises 401 if token invalid or expired.
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            os.getenv("JWT_SECRET"),
            algorithms=["HS256"]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

async def get_current_user_id(token_data: dict = Depends(verify_jwt)) -> str:
    """Extract user_id from verified JWT claims."""
    user_id = token_data.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user_id"
        )
    return user_id
```

**Alternatives Considered**:
1. **Third-party auth library** (e.g., `fastapi-users`, `authlib`)
   - Rejected: Over-engineered; we only need JWT verification, not full auth system
   - Authentication issuance is handled by Better Auth (Spec-2)
2. **Manual header parsing**
   - Rejected: FastAPI's HTTPBearer handles standard format automatically
3. **JWT validation per-endpoint**
   - Rejected: Not DRY; dependency injection centralizes logic

**Implementation Impact**: All protected endpoints use `current_user_id: str = Depends(get_current_user_id)`

---

### Q4: How should we design the database schema for user data isolation?

**Decision**: User table as foreign key reference, NOT managed by this service. Tasks table with `user_id` foreign key, composite index on `(user_id, id)`, and CHECK constraint

**Rationale**:
- User records managed by auth system (Spec-2), this API only references `user_id`
- Composite index `(user_id, id)` optimizes both list and single-task queries
- Database-level CHECK constraint prevents NULL `user_id` (defense in depth)
- All queries MUST include `WHERE user_id = $1` to enforce isolation

**Schema Design**:
```sql
-- Managed by Spec-2 (Better Auth)
-- We only reference user_id as UUID/string

-- Tasks table (this service)
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,  -- References users from auth system
    title VARCHAR(500) NOT NULL CHECK (length(trim(title)) > 0),
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT check_completed CHECK (
        (is_completed = FALSE AND completed_at IS NULL) OR
        (is_completed = TRUE AND completed_at IS NOT NULL)
    )
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_composite ON tasks(user_id, id);  -- Optimizes user-scoped lookups
CREATE INDEX idx_tasks_created ON tasks(created_at DESC);  -- Optimizes sorting
```

**Alternatives Considered**:
1. **UUID vs Integer IDs**
   - UUID chosen: Prevents ID enumeration attacks, distributed-friendly
   - Integer rejected: Easier to guess other users' task IDs
2. **Soft delete (deleted_at column)**
   - Rejected: Requirements specify hard delete (DELETE endpoint removes permanently)
   - Can be added later if needed
3. **Separate indexes** vs **composite index**
   - Composite chosen: Single index serves both `WHERE user_id =` and `WHERE user_id = AND id =`

**Implementation Impact**: SQLModel models must match this schema exactly

---

### Q5: What should the API response format and error handling look like?

**Decision**: Standardized JSON response envelope with consistent error structure

**Success Response Format**:
```json
{
  "data": { ... },  // or array for list endpoints
  "meta": {
    "timestamp": "2026-01-14T10:30:00Z",
    "request_id": "uuid"
  }
}
```

**Error Response Format**:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token",
    "details": null,  // Optional validation details
    "timestamp": "2026-01-14T10:30:00Z",
    "request_id": "uuid"
  }
}
```

**Error Code Taxonomy**:
- `401 UNAUTHORIZED`: Missing/invalid/expired JWT
- `403 FORBIDDEN`: Valid JWT but user_id mismatch (accessing other user's data)
- `404 NOT_FOUND`: Task doesn't exist or doesn't belong to authenticated user
- `400 BAD_REQUEST`: Validation failure (empty title, invalid format)
- `500 INTERNAL_SERVER_ERROR`: Unexpected server error
- `503 SERVICE_UNAVAILABLE`: Database connection failure

**Rationale**:
- Envelope pattern provides metadata without polluting business data
- Consistent error structure aids debugging and client error handling
- Request ID enables tracing through logs
- HTTP status codes follow REST conventions
- Detailed validation errors help frontend display field-level feedback

**Alternatives Considered**:
1. **Bare responses** (no envelope)
   - Rejected: No place for metadata like request_id or timestamps
2. **Problem Details for HTTP APIs** (RFC 7807)
   - Considered but rejected: More verbose than needed for this simple API
3. **Error codes in response body** vs **HTTP status only**
   - Chosen both: HTTP status for protocol, error code for application logic

**Implementation Impact**: Custom FastAPI exception handlers for consistent formatting

---

### Q6: How should we handle database connections and connection pooling?

**Decision**: SQLAlchemy async engine with connection pooling (pool_size=10, max_overflow=20)

**Configuration**:
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")  # Neon PostgreSQL connection string
# Example: postgresql+asyncpg://user:pass@host/db

engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set True for SQL logging in dev
    pool_size=10,  # Minimum connections
    max_overflow=20,  # Additional connections under load
    pool_pre_ping=True,  # Verify connections before use (handle Neon serverless wakeup)
    pool_recycle=3600,  # Recycle connections after 1 hour (Neon recommendation)
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

**Rationale**:
- Neon Serverless PostgreSQL may scale to zero; `pool_pre_ping=True` handles reconnection
- `pool_recycle=3600` aligns with Neon's connection lifecycle recommendations
- Async engine required for FastAPI's async endpoints
- Pool size 10+20 handles NFR-003 (100 concurrent users) efficiently

**Alternatives Considered**:
1. **No pooling** (new connection per request)
   - Rejected: High overhead, poor performance under load
2. **Larger pool sizes**
   - Rejected: Neon has connection limits; over-pooling wastes resources
3. **Sync SQLAlchemy**
   - Rejected: Would block event loop, terrible for FastAPI performance

**Implementation Impact**: Database sessions injected via dependency: `db: AsyncSession = Depends(get_db)`

---

### Q7: How should we structure the codebase for maintainability?

**Decision**: Layered architecture with clear separation: models → repositories → services → routers

**Directory Structure**:
```text
backend/
├── src/
│   ├── main.py                    # FastAPI app initialization
│   ├── config.py                  # Settings and environment variables
│   ├── database.py                # Database engine and session management
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py                # SQLModel Task model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── task.py                # Pydantic request/response schemas
│   │   └── error.py               # Error response schemas
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── task_repository.py     # Database query logic
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py        # Business logic
│   ├── routers/
│   │   ├── __init__.py
│   │   └── tasks.py               # API endpoints
│   ├── auth/
│   │   ├── __init__.py
│   │   └── dependencies.py        # JWT verification dependencies
│   └── middleware/
│       ├── __init__.py
│       ├── error_handler.py       # Global exception handlers
│       └── request_id.py          # Request ID middleware
├── tests/
│   ├── contract/                  # API contract tests
│   ├── integration/               # End-to-end tests
│   └── unit/                      # Unit tests per layer
├── .env.example                   # Example environment variables
├── pyproject.toml                 # Dependencies and project metadata
└── README.md                      # Backend-specific documentation
```

**Layer Responsibilities**:
- **Models**: SQLModel definitions (database schema)
- **Schemas**: Pydantic models for API requests/responses (validation)
- **Repositories**: Database queries (SELECT, INSERT, UPDATE, DELETE)
- **Services**: Business logic (authorization checks, validation, orchestration)
- **Routers**: FastAPI endpoints (HTTP handling, dependency injection)

**Rationale**:
- Clear separation makes testing easier (mock dependencies per layer)
- Repositories isolate SQL; swapping databases only affects this layer
- Services can be reused by multiple routers (e.g., background tasks)
- Matches Constitution Principle III (Separation of Concerns)

**Alternatives Considered**:
1. **Flat structure** (all code in `src/`)
   - Rejected: Doesn't scale, hard to navigate
2. **Feature-based structure** (`src/tasks/` containing all layers)
   - Rejected: Only one entity (Task) makes this premature
3. **Domain-Driven Design** (complex layering)
   - Rejected: Over-engineered for CRUD API

**Implementation Impact**: Import paths reflect layer hierarchy; tests organized by layer

---

## Technology Stack Summary

| Component | Technology | Version | Rationale |
|-----------|------------|---------|-----------|
| Language | Python | 3.11+ | Performance, async support |
| Framework | FastAPI | 0.109+ | Async, type hints, auto docs |
| ORM | SQLModel | 0.0.14+ | Type safety, Pydantic integration |
| Database | PostgreSQL | 15+ | Required by Neon Serverless |
| DB Driver | asyncpg | 0.29+ | Async driver for PostgreSQL |
| JWT Library | python-jose | 3.3+ | Industry standard JWT handling |
| Server | Uvicorn | 0.27+ | ASGI server for FastAPI |
| Testing | pytest | 8.0+ | De facto Python testing standard |
| Testing (Async) | pytest-asyncio | 0.23+ | Async test support |

## Dependencies

```toml
[project]
name = "todo-backend"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    "fastapi>=0.109.0",
    "sqlmodel>=0.0.14",
    "asyncpg>=0.29.0",
    "uvicorn[standard]>=0.27.0",
    "python-jose[cryptography]>=3.3.0",
    "python-multipart>=0.0.6",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.26.0",  # For FastAPI test client
    "ruff>=0.1.0",    # Linting
    "black>=24.0.0",  # Formatting
]
```

## Environment Variables

```bash
# .env.example
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
JWT_SECRET=your-secret-key-min-32-chars
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## Key Implementation Notes

1. **All database queries MUST filter by `user_id`** - No exceptions (Constitution Security-First)
2. **JWT validation happens via dependency injection** - Never optional
3. **URL `user_id` MUST match JWT `user_id`** - Return 403 if mismatch
4. **Use async/await consistently** - Never block the event loop
5. **Connection pooling configured for Neon** - `pool_pre_ping` and `pool_recycle`
6. **Type hints everywhere** - FastAPI + SQLModel + Pydantic enforces types
7. **Error responses follow standard format** - Use custom exception handlers

## Performance Considerations

- **Target**: <200ms p95 latency (NFR-001)
- **Strategy**:
  - Composite index `(user_id, id)` for fast lookups
  - Connection pooling reduces connection overhead
  - Async operations prevent blocking
  - Limit query results (pagination) for large datasets
  - Use `SELECT` only needed columns (avoid `SELECT *`)

## Security Considerations

- **JWT secret** stored in environment variable (never in code)
- **Database credentials** in environment variable (never in code)
- **SQL injection** prevented by SQLModel parameterized queries
- **User data isolation** enforced at database + application layers
- **Error messages** don't leak sensitive information (e.g., "user exists")
- **CORS** configured to whitelist only known frontend origins

## Next Steps

1. Create `data-model.md` - SQLModel definitions for Task entity
2. Create `contracts/` - OpenAPI specifications for all 6 endpoints
3. Create `quickstart.md` - Developer setup and testing guide
4. Update agent context with technology choices
