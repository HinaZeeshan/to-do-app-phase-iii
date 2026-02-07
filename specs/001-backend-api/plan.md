# Implementation Plan: Backend API & Database

**Branch**: `001-backend-api` | **Date**: 2026-01-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-backend-api/spec.md`

## Summary

Implement a secure, RESTful backend API using FastAPI and Neon Serverless PostgreSQL for multi-user task management. The API provides 6 CRUD endpoints with JWT-based authentication validation and strict user-level data isolation. All endpoints enforce zero-trust security: JWT validation on every request, URL `user_id` must match JWT claims, and database queries filtered by authenticated `user_id`. Task data persists in PostgreSQL with SQLModel ORM, featuring indexed queries for performance (<200ms p95 latency target). Architecture follows layered pattern (models → repositories → services → routers) with async/await throughout for optimal FastAPI performance.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.109+, SQLModel 0.0.14+, asyncpg 0.29+, python-jose 3.3+, uvicorn 0.27+
**Storage**: Neon Serverless PostgreSQL 15+ with asyncpg driver
**Testing**: pytest 8.0+ with pytest-asyncio 0.23+ for async test support
**Target Platform**: Linux/Windows server (ASGI-compatible), containerized deployment (Docker recommended)
**Project Type**: Web application (backend-only; frontend is Spec-3)
**Performance Goals**: <200ms p95 latency, support 100 concurrent users, handle 1000 tasks per user without degradation
**Constraints**: JWT validation mandatory (no exceptions), all queries MUST filter by user_id, connection pooling configured for Neon serverless, CORS configured for known origins only
**Scale/Scope**: 100+ concurrent users, 1000+ tasks per user, 6 RESTful endpoints, single Task entity with User reference

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Spec-Driven Development (NON-NEGOTIABLE) ✅ PASS

- [x] Implementation follows spec.md requirements exactly
- [x] All endpoints match functional requirements FR-001 through FR-020
- [x] No deviation from specified API contracts
- [x] Tasks will be generated from this plan (tasks.md via /sp.tasks)

**Status**: Compliant. All endpoints defined in spec.md, no scope creep.

### II. Security-First Architecture ✅ PASS

- [x] JWT validation on every API request (via FastAPI dependencies)
- [x] User identity extracted from JWT claims only (never trusted from client)
- [x] URL `user_id` parameter validated against JWT `user_id` claim (403 if mismatch)
- [x] Database queries scoped by `user_id` (all queries include WHERE user_id = $1)
- [x] Zero cross-user access (enforced at application + database layers)
- [x] JWT secret externalized (environment variable, never hardcoded)

**Status**: Compliant. Zero-trust architecture enforced via dependency injection.

### III. Clear Separation of Concerns ✅ PASS

- [x] Backend (this feature) separated from frontend (Spec-3)
- [x] Authentication issuance delegated to Better Auth (Spec-2)
- [x] This API only validates JWT, does not issue tokens
- [x] Clear layer boundaries: models → repositories → services → routers
- [x] Communication via REST API contracts (defined in contracts/openapi.yaml)

**Status**: Compliant. Backend under `backend/` directory, frontend will be separate.

### IV. Performance-Conscious Design ✅ PASS

- [x] Performance targets defined (NFR-001: <200ms p95)
- [x] Optimizations identified: composite indexes, connection pooling, async queries
- [x] No feature changes during optimization phase
- [x] Measurements planned (load testing with Apache Bench / Locust)

**Status**: Compliant. Performance measured, not assumed.

### V. Deterministic and Reproducible Outputs ✅ PASS

- [x] All dependencies explicit (pyproject.toml)
- [x] Environment configuration externalized (.env file)
- [x] No hardcoded secrets (JWT_SECRET, DATABASE_URL from environment)
- [x] Database schema versioned (Alembic migrations)
- [x] Same inputs produce same outputs (deterministic JWT validation)

**Status**: Compliant. All configuration externalized.

### Gate Summary

**Overall Status**: ✅ ALL GATES PASS - Ready to proceed with implementation

No violations detected. Architecture aligns with all 5 constitution principles.

## Project Structure

### Documentation (this feature)

```text
specs/001-backend-api/
├── spec.md              # Feature specification
├── plan.md              # This file (/sp.plan output)
├── research.md          # Technical decisions and justifications
├── data-model.md        # SQLModel entity definitions
├── quickstart.md        # Developer onboarding guide
├── contracts/
│   └── openapi.yaml     # OpenAPI 3.1 specification
├── checklists/
│   └── requirements.md  # Spec quality validation
└── tasks.md             # (Future: /sp.tasks output)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── main.py                    # FastAPI app initialization, CORS, middleware
│   ├── config.py                  # Settings class (loads .env via pydantic-settings)
│   ├── database.py                # Async engine, session factory, get_db dependency
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py                # SQLModel Task table model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── task.py                # Pydantic TaskCreate, TaskUpdate, TaskResponse
│   │   └── error.py               # ErrorResponse schema
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── task_repository.py     # Async database queries (CRUD operations)
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py        # Business logic, authorization checks
│   ├── routers/
│   │   ├── __init__.py
│   │   └── tasks.py               # FastAPI router with 6 endpoints
│   ├── auth/
│   │   ├── __init__.py
│   │   └── dependencies.py        # verify_jwt, get_current_user_id dependencies
│   └── middleware/
│       ├── __init__.py
│       ├── error_handler.py       # Global exception handlers
│       └── request_id.py          # Request ID middleware (UUID per request)
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Shared fixtures (test DB, test client)
│   ├── contract/
│   │   ├── __init__.py
│   │   └── test_api_contracts.py  # Verify OpenAPI compliance
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_task_flows.py     # End-to-end user scenarios
│   └── unit/
│       ├── __init__.py
│       ├── test_task_repository.py
│       ├── test_task_service.py
│       └── test_task_router.py
├── alembic/                       # Database migrations
│   ├── versions/
│   │   └── 001_create_tasks_table.py
│   ├── env.py
│   └── alembic.ini
├── .env                           # Environment variables (NOT in git)
├── .env.example                   # Example template
├── .gitignore                     # Ignore .env, venv, __pycache__, etc.
├── pyproject.toml                 # Dependencies and project metadata
└── README.md                      # Backend-specific documentation
```

**Structure Decision**:

Selected **Option 2: Web application** structure with `backend/` at repository root.

**Rationale**:
- Frontend is separate feature (Spec-3), requires independent directory
- Clear boundary between backend and frontend codebases
- Enables parallel development (backend team vs frontend team)
- Matches Constitution Principle III (Separation of Concerns)
- Simplifies deployment (backend can be containerized independently)

**NOT using**:
- Single project structure: Would mix backend/frontend when frontend added
- Mobile + API structure: No mobile app in scope

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected - this section is empty.

## Architectural Decisions

### Decision 1: Layered Architecture (Models → Repositories → Services → Routers)

**Context**: Need clear separation of concerns for testability and maintainability.

**Decision**: Implement 4-layer architecture:
1. **Models**: SQLModel definitions (database schema)
2. **Repositories**: Database query logic (async SQL operations)
3. **Services**: Business logic (authorization, validation, orchestration)
4. **Routers**: HTTP handling (FastAPI endpoints, dependency injection)

**Rationale**:
- Each layer testable in isolation (mock dependencies)
- Repositories encapsulate SQL (easy to swap database if needed)
- Services reusable across multiple routers or background jobs
- Routers focus purely on HTTP concerns (status codes, headers)

**Tradeoffs**:
- **Pro**: Clear boundaries, easy to test, maintainable long-term
- **Con**: More files/boilerplate than flat structure
- **Rejected Alternative**: Flat structure (all code in routers) - doesn't scale, hard to test

**Impact**: Imports follow layer hierarchy, tests organized by layer

---

### Decision 2: JWT Validation via FastAPI Dependencies

**Context**: Every endpoint must validate JWT and extract user_id (FR-007, FR-008).

**Decision**: Implement as FastAPI dependencies:
```python
async def verify_jwt(credentials: HTTPAuthCredentials = Depends(security)) -> dict
async def get_current_user_id(token_data: dict = Depends(verify_jwt)) -> str
```

**Rationale**:
- FastAPI dependency injection makes auth testable (mock dependencies)
- Centralized JWT logic (not duplicated across endpoints)
- Type-safe (credentials validated by HTTPBearer)
- Automatic OpenAPI documentation (security scheme appears in Swagger)

**Tradeoffs**:
- **Pro**: DRY, testable, type-safe, auto-documented
- **Con**: Requires understanding FastAPI dependency injection
- **Rejected Alternative**: Per-endpoint JWT parsing - not DRY, error-prone

**Impact**: All protected endpoints use `current_user_id: str = Depends(get_current_user_id)`

---

### Decision 3: Async Everything (AsyncSession, async def, asyncpg)

**Context**: FastAPI is async-first; blocking operations kill performance.

**Decision**: Use async/await throughout:
- asyncpg driver (not psycopg2)
- AsyncSession from SQLAlchemy
- All endpoints and functions declared `async def`

**Rationale**:
- FastAPI runs on async event loop (ASGI)
- Blocking DB calls would prevent handling other requests
- Async allows 100 concurrent users with single process
- Meets NFR-003 (100 concurrent users) efficiently

**Tradeoffs**:
- **Pro**: Excellent performance, efficient resource usage
- **Con**: Slightly more complex than sync code (must await everywhere)
- **Rejected Alternative**: Sync code - would block event loop, terrible performance

**Impact**: All database operations use `await`, SQLAlchemy engine is async

---

### Decision 4: Composite Index (user_id, id) for Performance

**Context**: All queries filter by user_id; single-task queries filter by both user_id AND id.

**Decision**: Create composite index on `(user_id, id)` plus separate index on `created_at DESC`.

**Rationale**:
- Composite index covers both list queries (`WHERE user_id = $1`) and single-task queries (`WHERE user_id = $1 AND id = $2`)
- PostgreSQL can use composite index for prefix matches (user_id alone)
- `created_at DESC` index optimizes default sorting

**Tradeoffs**:
- **Pro**: Fast queries (O(log n) lookups), meets <200ms p95 target
- **Con**: Slightly more storage, slower writes (3 indexes to update)
- **Rejected Alternative**: Only `user_id` index - single-task queries would be slower

**Impact**: Database schema includes 3 indexes, query performance <50ms

---

### Decision 5: Connection Pooling for Neon Serverless

**Context**: Neon Serverless PostgreSQL may scale to zero; need resilient connection handling.

**Decision**: Configure SQLAlchemy with:
- `pool_size=10` (min connections)
- `max_overflow=20` (additional under load)
- `pool_pre_ping=True` (verify before use)
- `pool_recycle=3600` (recycle after 1 hour)

**Rationale**:
- `pool_pre_ping` handles Neon serverless wakeup gracefully
- `pool_recycle` aligns with Neon connection lifecycle
- Pool size balances performance (reuse) vs resource limits

**Tradeoffs**:
- **Pro**: Resilient to Neon serverless behavior, good performance
- **Con**: More complex configuration than simple connection-per-request
- **Rejected Alternative**: No pooling - high overhead, poor performance

**Impact**: Database engine configured in `database.py`, handles 100 concurrent users

---

## Phase 0: Research Summary

See [research.md](./research.md) for detailed technical decisions.

**Key Findings**:
1. **Python 3.11+** provides 10-60% performance improvement over 3.10
2. **asyncpg** required for async PostgreSQL (not psycopg2)
3. **python-jose** is industry standard for JWT in Python
4. **UUID task IDs** prevent enumeration attacks (better than integers)
5. **Composite index (user_id, id)** optimizes both list and single-task queries
6. **Layered architecture** (models/repos/services/routers) scales better than flat structure

**No unknowns remain** - all technical decisions resolved.

## Phase 1: Design Summary

See [data-model.md](./data-model.md) and [contracts/openapi.yaml](./contracts/openapi.yaml) for details.

### Entities

**Task**:
- Fields: id (UUID), user_id (UUID FK), title (string 1-500), is_completed (bool), completed_at (datetime), created_at, updated_at
- Validation: title not empty, completion consistency (completed_at non-null iff is_completed true)
- Relationships: Many-to-One with User (managed by Spec-2)

**User Reference** (not managed by this API):
- Only referenced as foreign key from auth system

### API Contracts

6 endpoints defined in OpenAPI 3.1 spec:

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/api/{user_id}/tasks` | List all user's tasks | Required |
| POST | `/api/{user_id}/tasks` | Create new task | Required |
| GET | `/api/{user_id}/tasks/{id}` | Get single task | Required |
| PUT | `/api/{user_id}/tasks/{id}` | Update task | Required |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task | Required |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Mark complete | Required |

**Response Format**: JSON envelope with `data` and `meta` (timestamp, request_id)

**Error Format**: JSON with `error` object (code, message, details, timestamp, request_id)

**Status Codes**: 200 (OK), 201 (Created), 204 (No Content), 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found), 500 (Internal Error), 503 (Service Unavailable)

## Implementation Phases

### Phase 0: Setup ✅ COMPLETED

**Goal**: Initialize project structure and dependencies

**Output**: [research.md](./research.md)

**Status**: Complete - all technical decisions documented

---

### Phase 1: Design ✅ COMPLETED

**Goal**: Define data models and API contracts

**Output**:
- [data-model.md](./data-model.md) - Entity definitions
- [contracts/openapi.yaml](./contracts/openapi.yaml) - API specification
- [quickstart.md](./quickstart.md) - Developer guide

**Status**: Complete - ready for implementation

---

### Phase 2: Implementation Tasks ⏳ NEXT

**Goal**: Generate concrete implementation tasks

**Command**: `/sp.tasks`

**Output**: `tasks.md` with dependency-ordered tasks

**Task Categories** (preview):
1. **Setup**: Project init, dependencies, environment
2. **Foundation**: Database connection, JWT middleware, error handlers
3. **Data Layer**: SQLModel models, Alembic migrations
4. **Repository Layer**: Database queries (async CRUD operations)
5. **Service Layer**: Business logic, authorization checks
6. **Router Layer**: FastAPI endpoints (6 endpoints)
7. **Testing**: Contract, integration, and unit tests
8. **Documentation**: README, API docs, deployment guide

**Status**: Awaiting `/sp.tasks` command

---

## Dependencies Matrix

| Category | Package | Version | Purpose |
|----------|---------|---------|---------|
| Framework | fastapi | >=0.109.0 | Web framework |
| ORM | sqlmodel | >=0.0.14 | Database models |
| DB Driver | asyncpg | >=0.29.0 | Async PostgreSQL |
| JWT | python-jose[cryptography] | >=3.3.0 | Token validation |
| Server | uvicorn[standard] | >=0.27.0 | ASGI server |
| Validation | pydantic | >=2.5.0 | Request/response schemas |
| Settings | pydantic-settings | >=2.1.0 | Environment config |
| Testing | pytest | >=8.0.0 | Test framework |
| Testing (Async) | pytest-asyncio | >=0.23.0 | Async test support |
| HTTP Client | httpx | >=0.26.0 | Test client |
| Linting | ruff | >=0.1.0 | Code linting |
| Formatting | black | >=24.0.0 | Code formatting |
| Migrations | alembic | >=1.13.0 | Database migrations |

**Installation**: `pip install -e ".[dev]"` from backend/pyproject.toml

---

## Environment Configuration

Required environment variables (`.env`):

```ini
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
# Example: postgresql+asyncpg://user:pass@ep-xxx.region.aws.neon.tech/dbname

# Security
JWT_SECRET=min-32-char-secret-key
# Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**Security Note**: `.env` file must be in `.gitignore` - never commit secrets

---

## Testing Strategy

### Contract Tests (tests/contract/)

**Purpose**: Verify API responses match OpenAPI specification

**Tools**: pytest + openapi-spec-validator

**Coverage**:
- All 6 endpoints return correct status codes
- Response schemas match OpenAPI definitions
- Error responses match error schema
- Required fields present, types correct

**Example**:
```python
def test_list_tasks_matches_openapi_schema(client, jwt_token):
    response = client.get("/api/{user_id}/tasks", headers={"Authorization": f"Bearer {jwt_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "meta" in data
    # Validate against OpenAPI schema
```

---

### Integration Tests (tests/integration/)

**Purpose**: Validate end-to-end user scenarios from spec.md

**Tools**: pytest + httpx TestClient + test database

**Coverage**:
- All 6 user stories from spec.md (P1/P2/P3)
- Cross-user access prevention (403 errors)
- Token expiration handling (401 errors)
- Data persistence verification
- Concurrent update safety

**Example**:
```python
async def test_user_story_1_view_tasks(client, user_a_token, user_a_id):
    """US1: View all personal tasks - only see own tasks"""
    # Create 3 tasks for user A
    # Create 2 tasks for user B
    # List tasks for user A
    # Assert: returns 3 tasks, all belong to user A, none from user B
```

---

### Unit Tests (tests/unit/)

**Purpose**: Test individual layers in isolation

**Tools**: pytest + pytest-asyncio + unittest.mock

**Coverage by Layer**:

1. **Repositories** (test_task_repository.py):
   - CRUD operations work correctly
   - Queries filter by user_id
   - Database errors handled gracefully

2. **Services** (test_task_service.py):
   - Business logic correct (e.g., completion timestamp set)
   - Authorization checks enforced (user_id mismatch rejected)
   - Validation logic works (empty title rejected)

3. **Routers** (test_task_router.py):
   - HTTP status codes correct
   - Response format matches schemas
   - Dependencies injected properly

**Example**:
```python
@pytest.mark.asyncio
async def test_repository_filters_by_user_id(mock_session):
    repo = TaskRepository(mock_session)
    tasks = await repo.list_tasks(user_id="user-a")
    # Assert: query included WHERE user_id = 'user-a'
```

---

## Performance Targets & Validation

### Targets (from NFR-001 to NFR-006)

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| p95 Latency (single task) | <200ms | Apache Bench under load |
| List 1000 tasks | No degradation | Load test with large dataset |
| Concurrent users | 100+ | Locust load testing |
| Query time (indexed) | <50ms | PostgreSQL EXPLAIN ANALYZE |
| Connection pooling | Efficient reuse | Monitor pool stats |

### Validation Plan

1. **Local Performance Test**:
   ```bash
   ab -n 1000 -c 10 -H "Authorization: Bearer TOKEN" http://localhost:8000/api/USER_ID/tasks
   ```
   Expected: >500 req/s, <50ms mean, <200ms p95

2. **Database Query Analysis**:
   ```sql
   EXPLAIN ANALYZE SELECT * FROM tasks WHERE user_id = 'xxx' AND id = 'yyy';
   ```
   Expected: Index Scan on idx_tasks_composite, <10ms execution

3. **Load Testing** (100 concurrent users):
   ```bash
   locust -f tests/performance/locustfile.py --users 100 --spawn-rate 10
   ```
   Expected: <200ms p95, <1% error rate

---

## Security Checklist

- [x] JWT secret in environment variable (never hardcoded)
- [x] Database credentials in environment variable
- [x] JWT validation on every endpoint (no exceptions)
- [x] URL user_id validated against JWT user_id (403 if mismatch)
- [x] All queries filter by user_id (zero cross-user access)
- [x] SQL injection prevented (SQLModel parameterized queries)
- [x] CORS configured (whitelist frontend origins only)
- [x] Error messages don't leak sensitive info
- [x] Passwords not logged (no JWT secrets in logs)
- [x] HTTPS required in production (enforced by deployment config)

---

## Deployment Considerations

### Docker Container (Recommended)

**Dockerfile**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/pyproject.toml .
RUN pip install -e .
COPY backend/src ./src
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Environment Variables**: Injected via Docker Compose or Kubernetes ConfigMap

---

### Database Migrations

**Pre-deployment**:
```bash
alembic upgrade head
```

**Post-deployment**: No automatic migrations (manual approval required)

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Neon serverless cold start latency | Medium | Medium | Connection pooling with pool_pre_ping |
| JWT secret leaked | Low | Critical | Rotate secret immediately, revoke all tokens |
| Database connection exhaustion | Low | High | Connection pooling (max 30 connections) |
| Cross-user data access bug | Low | Critical | Comprehensive integration tests, code review |
| Performance degrades with load | Medium | Medium | Load testing before production, caching strategy |

---

## Next Steps

1. **Run `/sp.tasks`** - Generate implementation tasks from this plan
2. **Review tasks.md** - Ensure tasks match plan and spec
3. **Run `/sp.implement`** - Begin implementation (execute tasks)
4. **Iterate** - Test, fix, optimize, deploy

**Status**: Plan complete, ready for task generation ✅
