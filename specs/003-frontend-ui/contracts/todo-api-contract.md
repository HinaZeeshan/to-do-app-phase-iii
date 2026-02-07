# API Contract: Todo Application Frontend-Backend Interface

## Overview

This document defines the API contract between the frontend and backend for the Todo application. All requests must include JWT authentication in the Authorization header.

## Authentication Headers

All authenticated requests must include:
```
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

## Endpoints

### Authentication

#### POST /api/auth/signup
Register a new user

**Request**:
```json
{
  "email": "user@example.com",
  "password": "secure_password_123"
}
```

**Response (200)**:
```json
{
  "user": {
    "id": "uuid-string",
    "email": "user@example.com"
  },
  "token": "jwt-token-string"
}
```

**Response (400)**:
```json
{
  "error": "Validation error message"
}
```

#### POST /api/auth/login
Authenticate user and return JWT token

**Request**:
```json
{
  "email": "user@example.com",
  "password": "secure_password_123"
}
```

**Response (200)**:
```json
{
  "user": {
    "id": "uuid-string",
    "email": "user@example.com"
  },
  "token": "jwt-token-string"
}
```

**Response (401)**:
```json
{
  "error": "Invalid credentials"
}
```

### Todo Management

#### GET /api/todos
Retrieve authenticated user's todos

**Headers**:
```
Authorization: Bearer {jwt_token}
```

**Response (200)**:
```json
{
  "todos": [
    {
      "id": "uuid-string",
      "title": "Todo title",
      "description": "Optional description",
      "completed": false,
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-01T00:00:00Z",
      "user_id": "user-uuid"
    }
  ]
}
```

**Response (401)**:
```json
{
  "error": "Unauthorized"
}
```

#### POST /api/todos
Create a new todo for authenticated user

**Headers**:
```
Authorization: Bearer {jwt_token}
```

**Request**:
```json
{
  "title": "New todo title",
  "description": "Optional description",
  "completed": false
}
```

**Response (201)**:
```json
{
  "todo": {
    "id": "new-uuid-string",
    "title": "New todo title",
    "description": "Optional description",
    "completed": false,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z",
    "user_id": "authenticated-user-uuid"
  }
}
```

#### PUT /api/todos/{id}
Update an existing todo

**Headers**:
```
Authorization: Bearer {jwt_token}
```

**Request**:
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "completed": true
}
```

**Response (200)**:
```json
{
  "todo": {
    "id": "existing-uuid-string",
    "title": "Updated title",
    "description": "Updated description",
    "completed": true,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-02T00:00:00Z", // Updated timestamp
    "user_id": "authenticated-user-uuid"
  }
}
```

#### PATCH /api/todos/{id}/toggle
Toggle completion status of a todo

**Headers**:
```
Authorization: Bearer {jwt_token}
```

**Response (200)**:
```json
{
  "todo": {
    "id": "existing-uuid-string",
    "title": "Todo title",
    "description": "Todo description",
    "completed": true, // Toggled status
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-02T00:00:00Z",
    "user_id": "authenticated-user-uuid"
  }
}
```

#### DELETE /api/todos/{id}
Delete a todo

**Headers**:
```
Authorization: Bearer {jwt_token}
```

**Response (204)**:
No content returned

**Response (404)**:
```json
{
  "error": "Todo not found"
}
```

## Error Responses

Standard error format for all endpoints:

```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE_STRING"
}
```

## Status Codes

- `200`: Success for GET, PUT, PATCH requests
- `201`: Created for POST requests
- `204`: No content for successful DELETE requests
- `400`: Bad request - validation error
- `401`: Unauthorized - invalid or missing JWT
- `403`: Forbidden - user not authorized for resource
- `404`: Not found - requested resource doesn't exist
- `500`: Internal server error

## Rate Limiting

All authenticated endpoints are subject to rate limiting:
- 100 requests per minute per authenticated user
- Exceeding limits returns 429 status code