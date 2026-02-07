# Data Model: Authentication & JWT Security

## Entity: User

**Purpose**: Represents an authenticated user account with credentials

**Attributes**:

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL, AUTO | `gen_random_uuid()` | Unique user identifier |
| `email` | String | UNIQUE, NOT NULL, MAX 255 chars | - | User email address (login identifier) |
| `password_hash` | String | NOT NULL, MAX 255 chars | - | Bcrypt/Argon2 hashed password (never store plaintext) |
| `created_at` | DateTime | NOT NULL, AUTO | `CURRENT_TIMESTAMP` | Account creation timestamp |
| `last_login` | DateTime | NULL | `null` | Timestamp of most recent successful login |
| `is_active` | Boolean | NOT NULL | `true` | Account active status (for soft deletes) |

**Validation Rules**:

1. **Email Validation**:
   - MUST match RFC 5322 email format
   - MUST be unique across all users (enforced by UNIQUE constraint)
   - MUST be lowercase (normalized before storage)

2. **Password Requirements**:
   - Minimum 8 characters
   - At least one uppercase letter (A-Z)
   - At least one lowercase letter (a-z)
   - At least one number (0-9)
   - No maximum length (allow passphrases)

3. **Password Hashing**:
   - MUST use bcrypt with cost factor 12 or Argon2id
   - MUST include random salt (automatic with bcrypt/argon2)
   - NEVER store plaintext passwords
   - Hash computed by Better Auth automatically

**Relationships**:
- **User → Task**: One-to-Many (one user owns many tasks)
  - Foreign key: `task.user_id` references `user.id`
  - Cascade: ON DELETE CASCADE (deleting user deletes all their tasks)

**SQLModel Definition**:
```python
# backend/src/models/user.py
from sqlmodel import Field, SQLModel
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class User(SQLModel, table=True):
    """
    User model representing an authenticated account.
    Password hashing managed by Better Auth; this is schema definition only.
    """
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, nullable=False, unique=True, index=True)
    password_hash: str = Field(max_length=255, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    last_login: Optional[datetime] = Field(default=None, nullable=True)
    is_active: bool = Field(default=True, nullable=False)
```

**Database Schema (SQL)**:
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    -- Validation constraints
    CONSTRAINT check_email_format
        CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT check_email_lowercase
        CHECK (email = LOWER(email))
);

-- Index for fast login lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);
```

## Entity: AuthenticationSession (JWT Token - Not Stored)

**Purpose**: Represents active user session via JWT token (stateless, not persisted)

**JWT Claims**:

| Claim | Type | Description |
|-------|------|-------------|
| `user_id` | UUID (string) | User identifier from `users.id` |
| `email` | String | User email (for logging/auditing) |
| `iat` | Integer | Issued at timestamp (Unix epoch seconds) |
| `exp` | Integer | Expiration timestamp (Unix epoch seconds) |

**Token Properties**:
- Algorithm: HS256 (HMAC with SHA-256)
- Secret: Shared between Better Auth and FastAPI (environment variable)
- Lifetime: 24 hours (86400 seconds)
- Storage: HTTP-only cookie (`auth-token`) managed by Better Auth
- Transport: `Authorization: Bearer <token>` header for API requests

**Security Properties**:
- Signed (integrity protection via HMAC)
- Not encrypted (claims are readable if decoded)
- Stateless (no server-side session store required)
- Revocation: Not supported in MVP (token valid until expiration)

## Entity: AuthenticationEvent (Audit Log)

**Purpose**: Tracks authentication events for security monitoring and forensics

**Attributes**:

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL, AUTO | `gen_random_uuid()` | Event identifier |
| `user_id` | UUID | NULL (NULL if login failed) | - | Associated user (if event succeeded) |
| `event_type` | Enum | NOT NULL | - | Event type: `signup`, `login`, `logout`, `login_failed` |
| `ip_address` | String | NULL, MAX 45 chars | - | Client IP address (IPv4 or IPv6) |
| `user_agent` | String | NULL, MAX 500 chars | - | Browser user agent string |
| `success` | Boolean | NOT NULL | - | Whether event succeeded |
| `failure_reason` | String | NULL, MAX 255 chars | - | Error code if event failed |
| `created_at` | DateTime | NOT NULL, AUTO | `CURRENT_TIMESTAMP` | Event timestamp |

**Purpose**: Security monitoring, rate limiting enforcement, post-incident analysis

**SQLModel Definition**:
```python
# backend/src/models/auth_event.py
from sqlmodel import Field, SQLModel, Enum
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
import enum

class EventType(str, enum.Enum):
    SIGNUP = "signup"
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"

class AuthenticationEvent(SQLModel, table=True):
    """Authentication event log for security monitoring."""
    __tablename__ = "auth_events"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: Optional[UUID] = Field(default=None, nullable=True, index=True)
    event_type: EventType = Field(nullable=False, index=True)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    success: bool = Field(nullable=False)
    failure_reason: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
```

## Database Migration

**Alembic Migration** (`002_create_users_table.py`):
```python
def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),

        sa.UniqueConstraint('email', name='uq_users_email'),
        sa.CheckConstraint('email = LOWER(email)', name='check_email_lowercase'),
    )

    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_active', 'users', ['is_active'])

    # Add foreign key to tasks table (already exists from Spec-1)
    op.create_foreign_key(
        'fk_tasks_user_id',
        'tasks', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

    # Create auth_events table
    op.create_table(
        'auth_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('failure_reason', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_index('idx_auth_events_user_id', 'auth_events', ['user_id'])
    op.create_index('idx_auth_events_type', 'auth_events', ['event_type'])
    op.create_index('idx_auth_events_created_at', 'auth_events', ['created_at'])
```