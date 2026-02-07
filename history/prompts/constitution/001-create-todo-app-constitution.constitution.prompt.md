---
id: 001
title: Create Todo App Constitution
stage: constitution
date: 2026-01-14
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: system
command: /sp.constitution
labels: ["constitution", "initialization", "governance", "architecture", "security"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - None
---

## Prompt

/sp.constitution

Project: Todo Full-Stack Web Application (Hackathon – Phase II)

Specs:
- Spec-1: Backend API & Database
- Spec-2: Authentication & JWT Security
- Spec-3: Frontend UI & UX

---

Core principles:
- Spec-driven development (no manual coding)
- Security-first architecture for multi-user systems
- Clear separation of concerns between frontend, backend, and auth
- Performance-conscious design without feature changes
- Deterministic and reproducible outputs via Claude Code

---

Key standards:

### Architecture & Design
- Follow RESTful API design principles
- Enforce strict separation between frontend (Next.js) and backend (FastAPI)
- Use JWT as the single source of truth for user identity
- Ensure user data isolation at the database and API levels
- Maintain consistency across all specs

### Backend & Database (Spec-1)
- All task data must persist in Neon Serverless PostgreSQL
- ORM must be SQLModel
- Every API endpoint must validate authenticated user identity
- API responses must be predictable, structured, and typed
- No cross-user data access under any condition

### Authentication & Security (Spec-2)
- Authentication must be implemented using Better Auth
- JWT tokens must be issued on successful login
- JWT verification must occur on every protected API request
- Backend must validate token signature using shared secret
- User identity must be derived only from verified JWT claims
- URL `user_id` must match JWT `user_id`

### Frontend UI & UX (Spec-3)
- Frontend must be built with Next.js 16+ App Router
- UI must be responsive (mobile-first)
- Authentication state must be respected across routes
- API calls must include JWT in Authorization header
- UI must reflect loading, error, and empty states clearly
- No hardcoded user identifiers allowed

---

Constraints:
- No manual coding allowed (Claude Code only)
- Must follow Agentic Dev Stack workflow:
  Spec → Plan → Tasks → Implementation
- No deviation from defined specs
- No feature creep beyond Basic Level requirements

## Response snapshot

Created comprehensive project constitution v1.0.0 for Todo Full-Stack Web Application with the following structure:

**Core Principles (5)**:
1. Spec-Driven Development (NON-NEGOTIABLE) - Strict workflow: Specification → Planning → Tasks → Implementation
2. Security-First Architecture - Better Auth, JWT tokens, user data isolation, zero cross-user access
3. Clear Separation of Concerns - Frontend (Next.js) | Backend (FastAPI) | Auth (Better Auth)
4. Performance-Conscious Design - Optimizations without feature changes, measurement-required
5. Deterministic and Reproducible Outputs - No hardcoded values, externalized config

**Architecture & Technology Standards**:
- Backend: FastAPI + Neon PostgreSQL + SQLModel + Better Auth
- Frontend: Next.js 16+ App Router, mobile-first responsive design
- API: RESTful, JWT Bearer tokens, typed JSON responses

**Security Requirements**:
- Detailed 7-step authentication flow from credentials to scoped data operations
- Authorization rules: JWT claims as single source of truth, URL validation, filtered queries
- Data protection: .env secrets, credential rotation, JWT security, HTTPS, CORS

**Development Workflow**:
- Agentic Dev Stack phases: /sp.specify → /sp.plan → /sp.tasks → /sp.implement
- Agent delegation for Auth, FastAPI Backend, Frontend, and DB work
- PHR creation for every interaction (routed to constitution/feature/general)
- ADR suggestions for significant decisions (3-part significance test)

**Code Quality & Testing**:
- Type hints (Python), TypeScript preferred (Next.js), linting/formatting enforced
- Contract tests + Integration tests (unit tests optional)
- Performance targets: <200ms p95 API, <3s initial load, indexed queries

**Governance**:
- Semantic versioning (MAJOR.MINOR.PATCH)
- Amendment process with ADR linkage
- Compliance verification in all PRs
- Constitution supersedes all other practices

**Sync Impact Report** included as HTML comment documenting version, changes, template updates, and follow-ups.

## Outcome

- ✅ Impact: Established constitutional foundation for Todo Full-Stack Web Application with 5 core principles, complete technology standards, security requirements, development workflow, and governance model
- 🧪 Tests: None (constitution document - no executable tests)
- 📁 Files: Created .specify/memory/constitution.md (v1.0.0, 232 lines)
- 🔁 Next prompts: /sp.specify for Spec-1 (Backend API & Database), /sp.specify for Spec-2 (Authentication & JWT Security), /sp.specify for Spec-3 (Frontend UI & UX)
- 🧠 Reflection: Constitution provides clear guardrails for multi-user security, agent delegation patterns, and spec-driven development. All placeholders resolved with no TODOs. Template alignment verified.

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution created successfully with all requirements captured
- Graders run and results (PASS/FAIL): Constitutional compliance check - PASS (all templates aligned, no unresolved placeholders)
- Prompt variant (if applicable): Standard /sp.constitution workflow
- Next experiment (smallest change to try): Create first feature spec using /sp.specify to validate constitution principles in practice
