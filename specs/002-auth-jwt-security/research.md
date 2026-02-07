# Research: Authentication & JWT Security

## R1: Better Auth Configuration for Next.js

**Decision**: Use Better Auth as a standalone authentication provider integrated with Next.js App Router API routes

**Configuration Approach**:
```typescript
// frontend/lib/auth.ts
import { BetterAuth } from "better-auth"
import { nextCookies } from "better-auth/plugins"

export const auth = BetterAuth({
  database: {
    provider: "postgres",
    url: process.env.DATABASE_URL, // Same Neon DB as backend
  },
  secret: process.env.JWT_SECRET, // Shared secret with backend
  session: {
    expiresIn: 60 * 60 * 24, // 24 hours in seconds
    updateAge: 60 * 60, // Update session every hour
  },
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
    requireEmailVerification: false, // P3 feature
  },
  plugins: [
    nextCookies() // HTTP-only cookie management
  ],
  advanced: {
    generateId: () => crypto.randomUUID(), // UUID for user_id
  }
})
```

**Rationale**:
- Better Auth provides out-of-the-box JWT issuance with customizable claims
- `nextCookies` plugin handles secure HTTP-only cookie storage automatically
- Database integration ensures users persist to same Neon PostgreSQL as tasks
- Shared `JWT_SECRET` enables backend to verify tokens without API calls

**Alternatives Rejected**:
- NextAuth.js: More complex, designed for OAuth flows (overkill for email/password)
- Custom JWT implementation: Reinventing the wheel, higher security risk
- Third-party auth service (Auth0, Clerk): Introduces external dependency and cost

## R2: JWT Payload Structure

**Decision**: Standardize JWT payload with required claims matching backend expectations

**Payload Structure**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "iat": 1736857200,
  "exp": 1736943600
}
```

**Required Claims**:
- `user_id` (string/UUID): Primary user identifier, extracted by backend via `get_current_user_id` dependency
- `email` (string): User's email address for auditing/logging
- `iat` (integer): Issued at timestamp (Unix epoch)
- `exp` (integer): Expiration timestamp (Unix epoch)

**Rationale**:
- Backend already expects `user_id` claim (see H:\\phase-ii\\backend\\src\\auth\\dependencies.py line 59)
- UUID format matches `Task.user_id` foreign key type
- Minimal payload reduces token size and information leakage
- Standard JWT claims (`iat`, `exp`) enable automatic expiration validation

**Security Considerations**:
- No sensitive data in JWT (passwords, PII beyond email)
- Token is proof of authentication, not a data transport mechanism
- Backend re-validates token signature on every request (no trust of client)

## R3: Token Expiration Strategy

**Decision**: 24-hour access tokens with optional refresh tokens (P3)

**Access Token Lifecycle**:
- Issued on signup or login
- Expires after 24 hours (86400 seconds)
- No automatic refresh in MVP (P1-P2)
- User must re-login after expiration

**Refresh Token Strategy (P3 - Out of MVP Scope)**:
- Long-lived refresh token (7 days) stored in separate HTTP-only cookie
- Refresh endpoint exchanges valid refresh token for new access token
- Refresh token rotation on each use (prevents replay attacks)

**Rationale**:
- 24-hour expiration balances security and user experience
- Shorter expiration reduces impact of token compromise
- Longer sessions acceptable for low-risk todo application
- Refresh tokens add complexity; defer to post-MVP

**Implementation**:
```typescript
// Better Auth automatically handles expiration via expiresIn config
session: {
  expiresIn: 60 * 60 * 24, // 24 hours
  updateAge: 60 * 60, // Refresh session if >1 hour since last update
}
```

## R4: Secret Key Sharing Strategy

**Decision**: Shared JWT secret via environment variables, never in code or version control

**Secret Management**:
```env
# .env (NOT committed to Git)
JWT_SECRET=your-super-secret-key-min-256-bits-random-string

# Frontend (.env.local)
JWT_SECRET=your-super-secret-key-min-256-bits-random-string
DATABASE_URL=postgresql://user:pass@neon-host/dbname

# Backend (.env)
JWT_SECRET=your-super-secret-key-min-256-bits-random-string
DATABASE_URL=postgresql://user:pass@neon-host/dbname
```

**Secret Requirements**:
- Minimum 256 bits (32 characters) of high-entropy randomness
- Generated via `openssl rand -base64 32` or equivalent
- Never committed to Git (`.env` in `.gitignore`)
- Rotated periodically (invalidates all existing tokens)

**Secret Distribution**:
- Development: Manual copying or shared secret manager (Doppler, 1Password)
- Production: Environment variables via hosting platform (Vercel, Railway)
- CI/CD: Secrets injected via GitHub Actions secrets or similar

**Rationale**:
- Shared secret enables stateless JWT verification (no database lookup)
- Backend verifies token signature without calling frontend or auth service
- Secret rotation invalidates all tokens (security incident response)
- Matches Constitution Principle V (Deterministic and Reproducible Outputs)

**Security Risk**:
- If secret compromised, attacker can forge valid JWTs
- Mitigation: Short token expiration, secret rotation, monitoring for unusual activity

## R5: Error Handling Patterns for Auth Failures

**Decision**: Consistent HTTP status codes with generic error messages (prevent information leakage)

**Error Response Format**:
```typescript
// Standardized error response schema
interface ErrorResponse {
  error: {
    code: string;        // Machine-readable error code
    message: string;     // User-friendly message
    details?: string;    // Optional technical details (dev mode only)
  };
  meta: {
    timestamp: string;   // ISO 8601 timestamp
    request_id?: string; // Trace ID for debugging
  };
};
```

**Status Code Mapping**:

| Scenario | Status Code | Error Code | Message |
|----------|-------------|------------|---------|
| Missing Authorization header | 401 | `AUTH_MISSING` | "Authentication required" |
| Invalid JWT signature | 401 | `AUTH_INVALID` | "Invalid or expired token" |
| Expired JWT | 401 | `AUTH_EXPIRED` | "Invalid or expired token" |
| Missing `user_id` claim | 401 | `AUTH_INVALID_CLAIMS` | "Invalid token format" |
| Incorrect password (login) | 401 | `AUTH_FAILED` | "Invalid credentials" |
| Non-existent email (login) | 401 | `AUTH_FAILED` | "Invalid credentials" |
| URL user_id ≠ JWT user_id | 403 | `AUTH_FORBIDDEN` | "Access denied" |
| Email already exists (signup) | 409 | `CONFLICT_EMAIL` | "Email already registered" |
| Weak password (signup) | 400 | `VALIDATION_PASSWORD` | "Password does not meet requirements" |
| Rate limit exceeded | 429 | `RATE_LIMIT_EXCEEDED` | "Too many requests. Try again later." |

**Rationale**:
- Generic messages prevent username enumeration attacks
- Consistent format simplifies frontend error handling
- Machine-readable codes enable localization and analytics
- Detailed errors only in development (never expose stack traces in production)

**Implementation**:
```typescript
// Frontend API client
async function login(email: string, password: string) {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error: ErrorResponse = await response.json();
    throw new AuthError(error.error.code, error.error.message);
  }

  return response.json();
}
```

## R6: Rate Limiting Strategy for Brute-Force Protection

**Decision**: Multi-layered rate limiting with exponential backoff

**Rate Limiting Layers**:

1. **Frontend Client-Side** (soft limit, user convenience):
   - Disable login button after 3 failed attempts
   - Show countdown timer (30 seconds) before re-enabling
   - Track attempts in component state (resets on page refresh)

2. **Backend API-Level** (hard limit, security enforcement):
   - Use `slowapi` library (FastAPI-compatible rate limiter)
   - IP-based rate limiting: 5 login attempts per IP per minute
   - Email-based rate limiting: 10 login attempts per email per hour
   - Global rate limit: 1000 requests per IP per hour (DDoS prevention)

3. **Database-Level Tracking** (forensic analysis):
   - Log all authentication events to `auth_events` table
   - Track: `user_id`, `event_type`, `ip_address`, `timestamp`, `success`
   - Enable post-incident analysis and suspicious activity detection

**Configuration**:
```python
# backend/src/middleware/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# Apply to auth endpoints
@app.post("/api/auth/login")
@limiter.limit("5/minute")  # 5 attempts per minute per IP
async def login(request: Request, credentials: LoginRequest):
    # Login logic
    pass
```

**Progressive Penalties**:
- Attempts 1-3: No penalty
- Attempts 4-5: 30-second cooldown
- Attempts 6-10: 5-minute cooldown
- Attempts 11+: 1-hour account lockout + email notification

**Rationale**:
- Defense in depth: Multiple layers prevent circumvention
- IP-based limiting stops distributed attacks
- Email-based limiting stops single-user targeted attacks
- Logging enables detection of credential stuffing campaigns

**Trade-offs**:
- Legitimate users may be temporarily locked out (false positives)
- Shared IPs (corporate NAT, VPNs) may trigger rate limits for many users
- Mitigation: CAPTCHA after 3 failed attempts (P3 enhancement)