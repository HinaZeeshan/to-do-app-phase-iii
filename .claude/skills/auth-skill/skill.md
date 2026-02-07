---
name: auth-skill
description: Implement secure, scalable authentication systems including login, signup, password hashing, JWT tokens, and Better Auth integration for modern web applications.
---

# Auth Skill – Authentication & Security Implementation

## Purpose
This skill focuses on **building and integrating secure authentication flows** in full-stack web applications.  
It is designed for scenarios involving **user identity management**, **session security**, and **token-based authorization**, especially when using **Better Auth** with a decoupled backend.

---

## Scope of the Skill

### 1. Signup
- Implement secure user registration flows
- Validate input data efficiently
- Prevent duplicate accounts
- Ensure proper error handling and feedback
- Minimize database and network overhead

### 2. Login
- Authenticate users using secure credential checks
- Integrate Better Auth login mechanisms
- Ensure fast and reliable session initialization
- Support token-based authentication flows

### 3. Password Hashing
- Use industry-standard hashing algorithms (bcrypt, argon2, or equivalent)
- Apply proper salting strategies
- Configure cost factors to balance security and performance
- Never store or transmit plaintext passwords

### 4. JWT Tokens
- Generate JWTs upon successful authentication
- Include essential claims only (user id, email, roles if needed)
- Configure access and refresh token lifetimes correctly
- Validate tokens securely on backend services
- Use `Authorization: Bearer <token>` convention consistently

### 5. Better Auth Integration
- Configure Better Auth on the frontend (Next.js App Router)
- Enable JWT issuance through Better Auth
- Share secret keys securely with backend services
- Integrate Better Auth sessions with external APIs (e.g., FastAPI)
- Ensure seamless frontend–backend authentication flow

---

## Instructions

1. **Authentication Flow Design**
   - Frontend handles user interaction and session creation via Better Auth
   - Backend verifies identity using JWT tokens
   - User identity must be derived from verified tokens, not client input

2. **Security Enforcement**
   - Always hash passwords before storage
   - Never expose secrets or private keys to the client
   - Enforce token verification on every protected API route

3. **Backend Verification**
   - Extract JWT from request headers
   - Verify signature using shared secret
   - Decode claims and match authenticated user with requested resources
   - Reject unauthorized or mismatched requests

---

## Best Practices

- Keep JWT payloads minimal to reduce overhead
- Separate access and refresh token responsibilities
- Rotate secrets periodically when possible
- Use HTTPS exclusively for authentication traffic
- Apply rate limiting to login and signup endpoints
- Log authentication failures without leaking sensitive data
- Follow the principle of least privilege for user access

---

## Example Authentication Flow

```text
User Signup/Login (Frontend)
        ↓
Better Auth creates session + issues JWT
        ↓
Frontend API request with Authorization header
        ↓
Backend verifies JWT signature
        ↓
User identity extracted from token
        ↓
Authorized access to protected resources
