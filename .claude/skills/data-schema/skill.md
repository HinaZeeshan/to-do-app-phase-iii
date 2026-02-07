---
name: database-schema
description: Design and implement efficient database schemas, tables, and migrations for scalable applications. Use for backend data modeling and persistence layers.
---

# Database Skill – Schema Design & Migrations

## Purpose
This skill focuses on **designing robust database schemas**, **creating tables**, and **managing migrations** in a way that ensures **data integrity, scalability, and long-term maintainability**.  
It is intended for use in production-grade applications where schema decisions directly impact performance and reliability.

---

## Instructions

### 1. Schema Design
- Identify core entities and their relationships
- Apply proper normalization (avoid redundancy, ensure consistency)
- Define clear primary keys and foreign keys
- Choose appropriate data types based on access patterns
- Design for future extensibility (avoid premature constraints)

### 2. Table Creation
- Create tables with explicit constraints
  - Primary keys
  - Foreign keys
  - Unique constraints
  - Indexes where required
- Enforce referential integrity at the database level
- Use naming conventions consistently (snake_case, pluralization rules)

### 3. Migrations
- Write forward-only, repeatable migrations
- Separate schema changes from data migrations when possible
- Ensure migrations are idempotent and reversible (when supported)
- Version and document all migrations clearly
- Validate migrations against staging before production

---

## Best Practices

- Prefer explicit schemas over implicit behavior
- Index columns used frequently in filters, joins, and ordering
- Avoid over-indexing; balance write vs read performance
- Keep tables focused on a single responsibility
- Use timestamps (`created_at`, `updated_at`) consistently
- Plan schema changes with backward compatibility in mind
- Treat migrations as part of the application lifecycle, not an afterthought

---

## Example Structure

```sql
-- users table
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- tasks table
CREATE TABLE tasks (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  title TEXT NOT NULL,
  completed BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
