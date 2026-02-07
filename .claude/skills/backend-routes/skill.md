---
name: backend-routes
description: Generate backend routes, handle request/response cycles, and connect applications to databases using clean, scalable backend architecture.
---

# Backend Skill – API Routes & Data Handling

## Purpose
This skill focuses on **building and managing backend functionality** for modern web applications.  
Use this skill when implementing **API routes, request/response handling, and database connectivity** in a structured, maintainable way.

---

## Instructions

### 1. Route Generation
- Create RESTful API endpoints (CRUD-based)
- Follow clear and consistent URL patterns
- Separate concerns by feature or resource
- Support versioning when required

### 2. Request & Response Handling
- Validate incoming request data
- Handle headers, query params, and path params correctly
- Return structured and meaningful HTTP responses
- Use proper HTTP status codes (200, 201, 400, 401, 404, 500)

### 3. Database Connectivity
- Establish secure database connections
- Use ORM or query builders where appropriate
- Map models/entities cleanly to database tables
- Ensure efficient querying and indexing
- Handle transactions and rollbacks safely

---

## Best Practices

- Keep route handlers thin; move logic to services
- Validate input at the boundary (API layer)
- Avoid blocking or long-running operations in requests
- Use environment variables for secrets and DB credentials
- Implement error handling and logging consistently
- Follow separation of concerns: routes → services → data layer

---

## Example Structure

```text
backend/
├─ routes/
│  └─ tasks.py
├─ models/
│  └─ task.py
├─ services/
│  └─ task_service.py
├─ database/
│  └─ connection.py
└─ main.py
