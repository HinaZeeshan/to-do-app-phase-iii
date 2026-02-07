---

description: "Task list for Authentication & JWT Security implementation"
---

# Tasks: Authentication & JWT Security

**Input**: Design documents from `/specs/002-auth-jwt-security/`
**Prerequisites**: plan.md (required), spec.md (required)

**Tests**: Not explicitly requested - tests are OPTIONAL for this feature

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/` (when frontend implemented in Spec-3)
- Paths assume backend directory at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment configuration

- [x] T001 Generate secure JWT secret (256+ bits) using `openssl rand -base64 32`
- [x] T002 [P] Add JWT_SECRET to backend/.env (never commit to Git)
- [x] T003 [P] Update backend/.env.example with JWT_SECRET placeholder and setup instructions
- [x] T004 [P] Verify backend/.gitignore excludes .env file

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create backend/src/models/user.py with SQLModel User class (id, email, password_hash, created_at, last_login, is_active)
- [x] T006 [P] Create backend/src/models/auth_event.py with SQLModel AuthenticationEvent class (id, user_id, event_type, ip_address, user_agent, success, failure_reason, created_at)
- [x] T007 Create Alembic migration backend/alembic/versions/002_create_users_table.py with users table, auth_events table, indexes (email, is_active), foreign key from tasks.user_id to users.id
- [x] T008 Verify backend/src/config.py has JWT_SECRET and JWT_ALGORITHM settings (already exists from Spec-1)
- [x] T009 Verify backend/src/auth/dependencies.py correctly extracts user_id claim from JWT (already exists from Spec-1)
- [x] T010 [P] Install slowapi library for rate limiting in backend/pyproject.toml dependencies
- [x] T011 [P] Create backend/src/middleware/rate_limit.py with Limiter configuration (key_func=get_remote_address)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - New User Signup (Priority: P1) 🎯 MVP

**Goal**: Users can create an account and receive a JWT token for immediate access

**Independent Test**: POST /api/auth/signup with valid email and password, verify 201 response with JWT token, verify user exists in database, verify auto-login works

### Implementation for User Story 1

- [x] T012 [P] [US1] Create backend/src/schemas/auth.py with SignupRequest Pydantic model (email, password fields with validation)
- [x] T013 [P] [US1] Create backend/src/schemas/auth.py SignupResponse Pydantic model (user_id, email, token fields)
- [x] T014 [US1] Create backend/src/repositories/user_repository.py with UserRepository class and async create_user method
- [x] T015 [US1] Create backend/src/services/auth_service.py with AuthService class and signup method (validates email uniqueness, hashes password, creates user, generates JWT)
- [x] T016 [US1] Create backend/src/routers/auth.py with FastAPI router and POST /api/auth/signup endpoint returning 201 Created
- [x] T017 [US1] Register auth router in backend/src/main.py with app.include_router
- [x] T018 [US1] Add password strength validation in signup endpoint (min 8 chars, 1 uppercase, 1 lowercase, 1 number)
- [x] T019 [US1] Add email format validation and lowercase normalization in signup endpoint
- [x] T020 [US1] Handle duplicate email error with 409 Conflict response

**Checkpoint**: At this point, User Story 1 should be fully functional - users can sign up and receive JWT tokens

---

## Phase 4: User Story 2 - Existing User Login (Priority: P1) 🎯 MVP

**Goal**: Existing users can authenticate and receive JWT token to access their tasks

**Independent Test**: Create user via signup, then POST /api/auth/login with correct credentials, verify 200 response with JWT token, verify last_login timestamp updated

### Implementation for User Story 2

- [x] T021 [US2] Add LoginRequest Pydantic model to backend/src/schemas/auth.py (email, password fields)
- [x] T022 [US2] Add LoginResponse Pydantic model to backend/src/schemas/auth.py (user_id, email, token fields)
- [x] T023 [US2] Add async get_user_by_email method to backend/src/repositories/user_repository.py
- [x] T024 [US2] Add async update_last_login method to backend/src/repositories/user_repository.py
- [x] T025 [US2] Add login method to backend/src/services/auth_service.py (verifies password, generates JWT, updates last_login)
- [x] T026 [US2] Add POST /api/auth/login endpoint to backend/src/routers/auth.py returning 200 OK with JWT token
- [x] T027 [US2] Handle incorrect password with 401 Unauthorized and generic error message (no information leakage)
- [x] T028 [US2] Handle non-existent email with 401 Unauthorized and generic error message
- [x] T029 [US2] Apply rate limiting to login endpoint (@limiter.limit("5/minute")) in backend/src/routers/auth.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - users can sign up and log in

---

## Phase 5: User Story 3 - Secure API Access (Priority: P1) 🎯 MVP

**Goal**: Backend verifies JWT on every request and enforces user_id matching for data isolation

**Independent Test**: Login to get JWT, make API request to /api/{user_id}/tasks with valid token, verify 200 response; attempt with expired token, verify 401; attempt with mismatched user_id, verify 403

### Implementation for User Story 3

- [x] T030 [US3] Verify backend/src/auth/dependencies.py verify_jwt function validates signature using JWT_SECRET (already implemented in Spec-1)
- [x] T031 [US3] Verify backend/src/auth/dependencies.py get_current_user_id function extracts user_id claim (already implemented in Spec-1)
- [x] T032 [US3] Verify backend/src/services/task_service.py validates URL user_id matches JWT user_id on all methods (already implemented in Spec-1)
- [x] T033 [US3] Test protected endpoint /api/{user_id}/tasks with valid JWT token - should return 200 OK
- [x] T034 [US3] Test protected endpoint with missing Authorization header - should return 401 Unauthorized
- [x] T035 [US3] Test protected endpoint with expired JWT token - should return 401 Unauthorized
- [x] T036 [US3] Test protected endpoint with user_id mismatch (JWT user_id A accessing user_id B resources) - should return 403 Forbidden
- [x] T037 [US3] Test protected endpoint with manipulated/forged JWT token - should return 401 Unauthorized

**Checkpoint**: At this point, all P1 MVP user stories are complete - authentication and secure API access working end-to-end

---

## Phase 6: User Story 4 - User Logout (Priority: P2)

**Goal**: Users can explicitly end their session by removing JWT token

**Independent Test**: Login to get JWT, call POST /api/auth/logout, verify 200 response, verify subsequent API requests with old token fail (client-side token removal)

### Implementation for User Story 4

- [x] T038 [US4] Add LogoutResponse Pydantic model to backend/src/schemas/auth.py (message field)
- [x] T039 [US4] Add POST /api/auth/logout endpoint to backend/src/routers/auth.py with get_current_user_id dependency (returns 200 OK with success message)
- [x] T040 [US4] Document in quickstart.md that logout is client-side token removal (JWT remains valid until expiration unless secret rotated)

**Checkpoint**: At this point, User Stories 1-4 are complete (3 P1, 1 P2)

---

## Phase 7: User Story 5 - Token Refresh (Priority: P3)

**Goal**: Users' sessions are automatically extended without requiring re-login

**Note**: This is a P3 enhancement, deferred from MVP. Implementation requires refresh token generation and rotation logic.

### Implementation for User Story 5

- [ ] T041 [US5] Design refresh token strategy (long-lived refresh token stored separately from access token)
- [ ] T042 [US5] Add refresh_token field to SignupResponse and LoginResponse schemas
- [ ] T043 [US5] Generate refresh token (longer expiration: 7 days) in auth_service.py signup and login methods
- [ ] T044 [US5] Create backend/src/models/refresh_token.py with SQLModel RefreshToken class (token_hash, user_id, expires_at, created_at)
- [ ] T045 [US5] Create Alembic migration for refresh_tokens table
- [ ] T046 [US5] Add POST /api/auth/refresh endpoint to backend/src/routers/auth.py (validates refresh token, issues new access token, rotates refresh token)
- [ ] T047 [US5] Add refresh token blacklisting on logout
- [ ] T048 [US5] Test token refresh flow: access token expires, refresh token used, new access token issued

**Checkpoint**: All user stories complete including token refresh enhancement

---

## Phase 8: Security & Observability

**Purpose**: Authentication event logging and security monitoring

- [x] T049 [P] Add async log_auth_event method to backend/src/repositories/auth_event_repository.py
- [x] T050 [P] Log successful signup events to auth_events table in auth_service.py signup method
- [x] T051 [P] Log successful login events to auth_events table in auth_service.py login method
- [x] T052 [P] Log failed login events to auth_events table in auth_service.py login method
- [x] T053 [P] Log logout events to auth_events table in auth_service.py logout method (when implemented)
- [x] T054 Verify rate limiting middleware logs rate limit violations
- [x] T055 Add monitoring query to detect suspicious auth patterns (multiple failed logins from same IP or for same email)

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and cross-cutting improvements

- [x] T056 [P] Update backend/README.md with authentication setup instructions
- [x] T057 [P] Create quickstart guide at specs/002-auth-jwt-security/quickstart.md with signup/login/logout test scenarios
- [x] T058 [P] Verify all authentication endpoints return consistent error format matching backend/src/schemas/error.py
- [x] T059 [P] Add comprehensive error messages for all validation failures in auth_service.py
- [x] T060 [P] Document JWT token format and claims in quickstart.md
- [x] T061 [P] Document rate limiting behavior and limits in quickstart.md
- [x] T062 Run end-to-end validation: signup → login → access protected API → logout

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Security & Observability (Phase 8)**: Can run in parallel with user story phases (logging integration happens per story)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (but integrates with User model from US1)
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (validates existing JWT code from Spec-1)
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories (but requires logout endpoint)
- **User Story 5 (P3)**: Depends on US1 and US2 being complete (builds on existing auth flow with refresh token addition)

**Note**: All user stories depend on User model created in Foundational phase (T005). In practice, complete Foundational phase first, then user stories can proceed in parallel.

### Within Each User Story

- Schemas before services
- Repositories before services
- Services before routers
- Router before registration in main.py
- Validation before error handling

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002-T004)
- Within Foundational, tasks T006, T010, T011 can run in parallel
- Once Foundational completes, user stories 1-4 can have their schemas/repositories implemented in parallel by different developers
- All Security & Observability tasks marked [P] can run in parallel (T049-T053)
- All Polish tasks marked [P] can run in parallel (T056-T061)

---

## Parallel Example: After Foundational Complete

Once Phase 2 (Foundational) is done:

```bash
# All user stories can work on their schemas in parallel:
# Team Member A: User Story 1 (signup)
# Team Member B: User Story 2 (login)
# Team Member C: User Story 4 (logout)

# Each works independently on their repository/service/router layers
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 3 Only - All P1)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T011) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 - Signup (T012-T020)
4. Complete Phase 4: User Story 2 - Login (T021-T029)
5. Complete Phase 5: User Story 3 - Secure API Access (T030-T037)
6. **STOP and VALIDATE**: Test all 3 P1 stories independently and together
7. Deploy/demo if ready

**MVP Scope**: 3 user stories (signup, login, secure API access) = 37 tasks

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (11 tasks)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP = signup only, 9 tasks)
3. Add User Story 2 → Test independently → Deploy/Demo (MVP = signup + login, 9 tasks)
4. Add User Story 3 → Test independently → Deploy/Demo (MVP = complete auth flow, 8 tasks)
5. Add User Story 4 → Test independently → Deploy/Demo (logout added, 3 tasks)
6. Add User Story 5 → Test independently → Deploy/Demo (token refresh added, 8 tasks)
7. Security & Observability → Monitoring enabled (7 tasks)
8. Polish → Final release (7 tasks)

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (11 tasks)
2. Developer A implements US1 Signup (T012-T020)
3. Developer B implements US2 Login (T021-T029)
4. Developer C implements US4 Logout (T038-T040)
5. Stories complete and integrate independently
6. Team validates US3 Secure API Access together (T030-T037) - mostly verification of existing Spec-1 code

---

## Task Count Summary

- **Setup**: 4 tasks
- **Foundational**: 7 tasks
- **User Story 1 (P1)**: 9 tasks
- **User Story 2 (P1)**: 9 tasks
- **User Story 3 (P1)**: 8 tasks
- **User Story 4 (P2)**: 3 tasks
- **User Story 5 (P3)**: 8 tasks
- **Security & Observability**: 7 tasks
- **Polish**: 7 tasks

**Total**: 62 tasks

**MVP Scope**: 11 (Setup + Foundational) + 9 (US1) + 9 (US2) + 8 (US3) = **37 tasks for MVP**

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All file paths are relative to repository root
- Database migrations must be run sequentially (not in parallel)
- User Story 3 mostly validates existing JWT code from Spec-1 (backend already has JWT verification)
