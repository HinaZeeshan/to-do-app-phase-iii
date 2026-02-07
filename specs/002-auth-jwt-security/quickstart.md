# Quickstart: Authentication & JWT Security

## Prerequisites

- Node.js 18+ (for Next.js frontend)
- Python 3.11+ (for FastAPI backend)
- Neon PostgreSQL database (from Spec-1)
- Environment variables configured

## Setup Steps

### 1. Generate JWT Secret

```bash
# Generate a secure 256-bit secret
openssl rand -base64 32
# Output: e.g., "O44EFS9ItmnFG57TKb5y9z0inwkVTw1HrWr3wj9mEOQ="
```

### 2. Configure Environment Variables

**Backend (.env)**:
```env
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/dbname
JWT_SECRET=O44EFS9ItmnFG57TKb5y9z0inwkVTw1HrWr3wj9mEOQ=
JWT_ALGORITHM=HS256
CORS_ORIGINS=http://localhost:3000
```

**Frontend (.env.local)**:
```env
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/dbname
JWT_SECRET=O44EFS9ItmnFG57TKb5y9z0inwkVTw1HrWr3wj9mEOQ=
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Database Migration

```bash
cd backend
alembic upgrade head  # Creates users and auth_events tables
```

### 4. Install Dependencies

**Backend**:
```bash
cd backend
pip install -e ".[dev]"
```

### 5. Start Development Server

**Backend**:
```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

## Testing Authentication Flow

### 1. Signup New User

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }'
```

Expected response:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "test@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 2. Login Existing User

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }'
```

### 3. Access Protected Backend API

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl http://localhost:8000/api/{user_id}/tasks \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Logout

```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

## JWT Token Format and Claims

JWT tokens contain the following claims:
- `user_id`: User identifier (UUID string)
- `email`: User email address
- `iat`: Issued at timestamp (Unix epoch)
- `exp`: Expiration timestamp (Unix epoch, 24 hours from issue)

## Rate Limiting Behavior

- Login attempts: 5 per minute per IP address
- Signup attempts: 5 per minute per IP address
- Rate limit exceeded: HTTP 429 status with "Too many requests" message

## Security Checklist

- [x] JWT_SECRET is 256+ bits of randomness
- [x] JWT_SECRET is NOT committed to Git
- [x] `.env` and `.env.local` are in `.gitignore`
- [x] CORS_ORIGINS is restricted to known domains (not "*")
- [x] HTTPS enabled in production
- [x] Rate limiting configured on login endpoint
- [x] Auth events logged to `auth_events` table