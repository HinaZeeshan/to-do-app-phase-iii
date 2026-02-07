# Data Model: Backend API & Database

**Feature**: Backend API & Database
**Branch**: 001-backend-api
**Date**: 2026-01-14
**Purpose**: Entity definitions, relationships, and validation rules

## Entities

### Task

**Purpose**: Represents a single task item belonging to a user

**Attributes**:

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL, AUTO | `gen_random_uuid()` | Unique task identifier |
| `user_id` | UUID | FOREIGN KEY, NOT NULL, INDEXED | - | Owner of the task (references auth system users) |
| `title` | String | NOT NULL, MAX 500 chars, NOT EMPTY | - | Task description/title |
| `is_completed` | Boolean | NOT NULL | `false` | Completion status |
| `completed_at` | DateTime | NULL, CONDITIONAL | `null` | Timestamp when task was marked complete |
| `created_at` | DateTime | NOT NULL, AUTO | `CURRENT_TIMESTAMP` | Creation timestamp |
| `updated_at` | DateTime | NOT NULL, AUTO-UPDATE | `CURRENT_TIMESTAMP` | Last modification timestamp |

**Validation Rules**:

1. **Title Validation**:
   - MUST NOT be empty string (after trimming whitespace)
   - MUST NOT exceed 500 characters
   - MUST be provided on creation

2. **Completion Consistency**:
   - IF `is_completed = false` THEN `completed_at MUST be null`
   - IF `is_completed = true` THEN `completed_at MUST NOT be null`
   - Enforced by database CHECK constraint

3. **User Association**:
   - `user_id` MUST NOT be null
   - `user_id` MUST reference existing user from authentication system
   - Enforced by foreign key constraint

**State Transitions**:

```
[New Task]
    ↓ (POST /api/{user_id}/tasks with title)
[Incomplete Task]
    ├─→ (PATCH /api/{user_id}/tasks/{id}/complete)
    ├─→ (PUT /api/{user_id}/tasks/{id} with is_completed=true)
    │       ↓
    │   [Complete Task]
    │       ├─→ (PUT /api/{user_id}/tasks/{id} with is_completed=false)
    │       │       ↓
    │       │   [Incomplete Task] (completed_at set to null)
    │       └─→ (DELETE /api/{user_id}/tasks/{id})
    │               ↓
    │           [Deleted] (permanent removal)
    └─→ (DELETE /api/{user_id}/tasks/{id})
            ↓
        [Deleted] (permanent removal)
```

**Indexes**:

1. **Primary Index**: `id` (automatic with PRIMARY KEY)
2. **User Isolation Index**: `user_id` (optimizes `WHERE user_id = $1`)
3. **Composite Index**: `(user_id, id)` (optimizes user-scoped single task lookups)
4. **Sorting Index**: `created_at DESC` (optimizes default list sorting)

**Relationships**:

- **User → Task**: One-to-Many (one user owns many tasks)
  - Foreign key: `task.user_id` references `user.id`
  - Cascade: ON DELETE CASCADE (deleting user deletes all their tasks)
  - Note: User entity managed by authentication system (Spec-2), not this API

---

### User Reference (Not Managed by This Service)

**Purpose**: Reference to authenticated user from Better Auth system

**Attributes**:

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | User unique identifier (from JWT claims `user_id`) |

**Note**: This API does NOT create, update, or delete users. User management is handled by the authentication system (Spec-2). This API only:
1. Receives `user_id` from validated JWT tokens
2. Uses `user_id` to scope all task queries
3. References `user_id` as foreign key in tasks table

---

## SQLModel Definitions

### Task Model (backend/src/models/task.py)

```python
from sqlmodel import Field, SQLModel
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class Task(SQLModel, table=True):
    """
    SQLModel for Task entity.
    Represents the database table schema.
    """
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    title: str = Field(max_length=500, nullable=False)
    is_completed: bool = Field(default=False, nullable=False)
    completed_at: Optional[datetime] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Buy groceries",
                "is_completed": False,
                "completed_at": None,
                "created_at": "2026-01-14T10:00:00Z",
                "updated_at": "2026-01-14T10:00:00Z"
            }
        }
```

### Request/Response Schemas (backend/src/schemas/task.py)

```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID
from typing import Optional

class TaskCreate(BaseModel):
    """Request schema for creating a new task."""
    title: str = Field(..., min_length=1, max_length=500, description="Task title")

    @validator("title")
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip()

class TaskUpdate(BaseModel):
    """Request schema for updating an existing task."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    is_completed: Optional[bool] = None

    @validator("title")
    def title_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip() if v else v

class TaskResponse(BaseModel):
    """Response schema for task data."""
    id: UUID
    user_id: UUID
    title: str
    is_completed: bool
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Allows conversion from SQLModel instances

class TaskListResponse(BaseModel):
    """Response schema for list of tasks."""
    data: list[TaskResponse]
    meta: dict = Field(default_factory=lambda: {
        "timestamp": datetime.utcnow().isoformat(),
        "count": 0
    })
```

---

## Database Schema (SQL)

```sql
-- Note: users table managed by authentication system (Spec-2)
-- Assuming users table exists with:
-- CREATE TABLE users (
--     id UUID PRIMARY KEY,
--     email VARCHAR(255) UNIQUE NOT NULL,
--     created_at TIMESTAMP NOT NULL
-- );

-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    title VARCHAR(500) NOT NULL,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraint (cascading delete)
    CONSTRAINT fk_user FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    -- Validation constraints
    CONSTRAINT check_title_not_empty
        CHECK (length(trim(title)) > 0),

    CONSTRAINT check_completion_consistency
        CHECK (
            (is_completed = FALSE AND completed_at IS NULL) OR
            (is_completed = TRUE AND completed_at IS NOT NULL)
        )
);

-- Indexes for performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_composite ON tasks(user_id, id);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);

-- Trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tasks_updated_at
BEFORE UPDATE ON tasks
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

---

## Migration Strategy

**Assumption**: Database migrations handled externally (not part of API runtime)

**Migration Tool**: Alembic (SQLAlchemy migration tool, compatible with SQLModel)

**Initial Migration** (001_create_tasks_table.py):
1. Create tasks table with all columns and constraints
2. Create indexes for performance
3. Create trigger for `updated_at` auto-update

**Future Migrations**:
- Add new columns (e.g., `priority`, `due_date`) as ALTER TABLE
- Use `alembic revision --autogenerate` to detect model changes
- Always test migrations on staging before production

---

## Data Validation Summary

### Application-Level Validation (Pydantic Schemas)

✅ Title length (1-500 characters)
✅ Title not empty after trimming
✅ UUID format validation (automatic via type hints)
✅ Request body structure validation (automatic via FastAPI)

### Database-Level Validation (PostgreSQL Constraints)

✅ Title NOT NULL
✅ Title not empty (CHECK constraint)
✅ user_id NOT NULL
✅ user_id references valid user (FOREIGN KEY)
✅ Completion consistency (CHECK constraint)
✅ Primary key uniqueness (UUID collision ~impossible)

### Defense in Depth

Both application and database layers validate data. If application validation is bypassed (e.g., direct database access), database constraints still enforce integrity.

---

## Query Patterns

### List All Tasks for User

```sql
SELECT * FROM tasks
WHERE user_id = $1
ORDER BY created_at DESC;
```

**Index Used**: `idx_tasks_user_id` + `idx_tasks_created_at`
**Performance**: O(log n) + O(m) where m = user's task count

### Get Single Task for User

```sql
SELECT * FROM tasks
WHERE user_id = $1 AND id = $2
LIMIT 1;
```

**Index Used**: `idx_tasks_composite (user_id, id)`
**Performance**: O(log n) - single index lookup

### Create Task

```sql
INSERT INTO tasks (user_id, title, is_completed, created_at, updated_at)
VALUES ($1, $2, FALSE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
RETURNING *;
```

**Performance**: O(log n) - index updates for new row

### Update Task

```sql
UPDATE tasks
SET title = $3, is_completed = $4, completed_at = $5, updated_at = CURRENT_TIMESTAMP
WHERE user_id = $1 AND id = $2
RETURNING *;
```

**Performance**: O(log n) - index lookup + update

### Delete Task

```sql
DELETE FROM tasks
WHERE user_id = $1 AND id = $2
RETURNING id;
```

**Performance**: O(log n) - index lookup + delete

### Mark Task Complete

```sql
UPDATE tasks
SET is_completed = TRUE, completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
WHERE user_id = $1 AND id = $2
RETURNING *;
```

**Performance**: O(log n) - same as update

---

## Security Considerations

1. **User Isolation**: ALL queries include `WHERE user_id = $1` - no exceptions
2. **UUID IDs**: Prevents task ID enumeration attacks
3. **Foreign Key Cascade**: Deleting user automatically deletes their tasks (cleanup)
4. **SQL Injection**: SQLModel uses parameterized queries (safe by default)
5. **Data Validation**: Both application and database layers validate inputs

---

## Performance Considerations

1. **Composite Index**: `(user_id, id)` covers most common query pattern
2. **Sorted Index**: `created_at DESC` optimizes default list sorting
3. **Connection Pooling**: Reuses database connections (configured in database.py)
4. **Async Queries**: Non-blocking database operations (asyncpg driver)
5. **Pagination**: List queries should implement LIMIT/OFFSET for large datasets

**Expected Query Times** (on indexed columns):
- List tasks: <50ms for up to 1000 tasks
- Get single task: <10ms
- Create task: <20ms
- Update task: <20ms
- Delete task: <15ms

---

## Testing Considerations

### Data Model Tests

1. **Field Validation**: Test Pydantic validators (empty title, max length)
2. **State Transitions**: Test is_completed ↔ completed_at consistency
3. **Relationships**: Test foreign key constraints (invalid user_id)
4. **Serialization**: Test SQLModel → Pydantic conversion

### Integration Tests

1. **User Isolation**: Verify queries only return user's own tasks
2. **Cross-User Access**: Verify 403 when accessing other user's tasks
3. **Concurrent Updates**: Test two users modifying different tasks simultaneously
4. **Database Constraints**: Test CHECK constraints enforce rules
