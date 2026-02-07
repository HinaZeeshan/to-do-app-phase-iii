---

description: "Task list for Backend API & Database implementation"
---

# Tasks: Backend API & Database

**Input**: Design documents from `/specs/001-backend-api/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested - tests are OPTIONAL for this feature

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `backend/tests/`
- Paths assume backend directory at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure with src/ and tests/ subdirectories
- [x] T002 [P] Create pyproject.toml with Python 3.11+ requirement and dependencies (fastapi, sqlmodel, asyncpg, python-jose, uvicorn, pydantic, pydantic-settings)
- [x] T003 [P] Create .env.example file with DATABASE_URL, JWT_SECRET, CORS_ORIGINS, ENVIRONMENT, LOG_LEVEL placeholders
- [x] T004 [P] Create .gitignore file to exclude .env, venv, __pycache__, .pytest_cache
- [x] T005 [P] Create backend/README.md with setup instructions and architecture overview

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create backend/src/config.py with Settings class using pydantic-settings to load environment variables
- [x] T007 Create backend/src/database.py with async SQLAlchemy engine, AsyncSessionLocal, and get_db dependency (pool_size=10, max_overflow=20, pool_pre_ping=True, pool_recycle=3600)
- [x] T008 [P] Create backend/src/auth/dependencies.py with verify_jwt and get_current_user_id async functions using python-jose
- [x] T009 [P] Create backend/src/middleware/error_handler.py with global exception handlers for HTTPException and generic exceptions
- [x] T010 [P] Create backend/src/middleware/request_id.py with middleware to add UUID request_id to each request
- [x] T011 [P] Create backend/src/schemas/error.py with ErrorResponse Pydantic model
- [x] T012 Create backend/src/main.py with FastAPI app initialization, CORS middleware, error handlers, and request_id middleware
- [x] T013 Initialize Alembic in backend/alembic/ directory with alembic init command
- [x] T014 Configure backend/alembic/env.py to use async engine and import SQLModel metadata
- [x] T015 Create backend/src/models/__init__.py as empty file
- [x] T016 Create backend/src/schemas/__init__.py as empty file
- [x] T017 Create backend/src/repositories/__init__.py as empty file
- [x] T018 Create backend/src/services/__init__.py as empty file
- [x] T019 Create backend/src/routers/__init__.py as empty file

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View All Personal Tasks (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can retrieve all their tasks sorted by creation date

**Independent Test**: Authenticate a user, create 3 tasks for that user, call GET /api/{user_id}/tasks, verify returns exactly 3 tasks belonging to that user and no tasks from other users

### Implementation for User Story 1

- [x] T020 [P] [US1] Create backend/src/models/task.py with SQLModel Task class (id, user_id, title, is_completed, completed_at, created_at, updated_at fields)
- [x] T021 [P] [US1] Create backend/src/schemas/task.py with TaskResponse and TaskListResponse Pydantic models
- [x] T022 [US1] Create Alembic migration in backend/alembic/versions/001_create_tasks_table.py with tasks table, indexes (user_id, composite user_id+id, created_at DESC), CHECK constraints, and updated_at trigger
- [x] T023 [US1] Apply migration with alembic upgrade head command
- [x] T024 [US1] Create backend/src/repositories/task_repository.py with TaskRepository class and async list_tasks method that filters by user_id and orders by created_at DESC
- [x] T025 [US1] Create backend/src/services/task_service.py with TaskService class and list_tasks method that validates user_id matches JWT claim
- [x] T026 [US1] Create backend/src/routers/tasks.py with FastAPI router and GET /api/{user_id}/tasks endpoint using get_current_user_id dependency
- [x] T027 [US1] Register tasks router in backend/src/main.py with app.include_router

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Create New Task (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can create new tasks with title validation

**Independent Test**: Authenticate a user, POST /api/{user_id}/tasks with title "Buy groceries", verify task appears in list with status incomplete

### Implementation for User Story 2

- [x] T028 [US2] Add TaskCreate Pydantic model to backend/src/schemas/task.py with title field validation (min_length=1, max_length=500, strip whitespace)
- [x] T029 [US2] Add async create_task method to backend/src/repositories/task_repository.py that inserts task with user_id and returns created task
- [x] T030 [US2] Add create_task method to backend/src/services/task_service.py that validates user_id match and title not empty
- [x] T031 [US2] Add POST /api/{user_id}/tasks endpoint to backend/src/routers/tasks.py that returns 201 Created with task details and validates user_id from JWT

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - View Single Task Details (Priority: P2)

**Goal**: Authenticated users can retrieve a specific task by ID

**Independent Test**: Create a task, capture its ID, GET /api/{user_id}/tasks/{id}, verify all attributes match

### Implementation for User Story 3

- [x] T032 [US3] Add async get_task_by_id method to backend/src/repositories/task_repository.py that filters by user_id AND id
- [x] T033 [US3] Add get_task method to backend/src/services/task_service.py that validates user_id match and returns 404 if not found
- [x] T034 [US3] Add GET /api/{user_id}/tasks/{id} endpoint to backend/src/routers/tasks.py that returns task or 404

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Update Task Details (Priority: P2)

**Goal**: Authenticated users can update task title and completion status

**Independent Test**: Create task with title "Buy milk", PUT /api/{user_id}/tasks/{id} with title "Buy almond milk", verify title changed

### Implementation for User Story 4

- [x] T035 [US4] Add TaskUpdate Pydantic model to backend/src/schemas/task.py with optional title and is_completed fields
- [x] T036 [US4] Add async update_task method to backend/src/repositories/task_repository.py that updates task and sets updated_at timestamp
- [x] T037 [US4] Add update_task method to backend/src/services/task_service.py that validates user_id match, handles 404, validates title if provided, and sets completed_at if is_completed changes
- [x] T038 [US4] Add PUT /api/{user_id}/tasks/{id} endpoint to backend/src/routers/tasks.py that returns updated task

**Checkpoint**: At this point, User Stories 1-4 should all work independently

---

## Phase 7: User Story 5 - Mark Task as Complete (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can mark tasks complete with single action

**Independent Test**: Create incomplete task, PATCH /api/{user_id}/tasks/{id}/complete, verify is_completed=true and completed_at timestamp set

### Implementation for User Story 5

- [x] T039 [US5] Add async complete_task method to backend/src/repositories/task_repository.py that sets is_completed=True and completed_at=now
- [x] T040 [US5] Add complete_task method to backend/src/services/task_service.py that validates user_id match and ensures idempotency (no error if already complete)
- [x] T041 [US5] Add PATCH /api/{user_id}/tasks/{id}/complete endpoint to backend/src/routers/tasks.py

**Checkpoint**: All P1 user stories (US1, US2, US5) are now complete - MVP is functional

---

## Phase 8: User Story 6 - Delete Task (Priority: P3)

**Goal**: Authenticated users can permanently delete tasks

**Independent Test**: Create task, capture ID, DELETE /api/{user_id}/tasks/{id}, verify 204 response and GET returns 404

### Implementation for User Story 6

- [x] T042 [US6] Add async delete_task method to backend/src/repositories/task_repository.py that deletes task by user_id and id
- [x] T043 [US6] Add delete_task method to backend/src/services/task_service.py that validates user_id match and returns 404 if not found
- [x] T044 [US6] Add DELETE /api/{user_id}/tasks/{id} endpoint to backend/src/routers/tasks.py that returns 204 No Content on success

**Checkpoint**: All user stories should now be independently functional

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T045 [P] Add comprehensive error messages to backend/src/services/task_service.py for all validation failures
- [x] T046 [P] Add request/response logging to backend/src/main.py middleware
- [x] T047 [P] Verify all endpoints return consistent error format matching backend/src/schemas/error.py
- [x] T048 [P] Add startup event handler to backend/src/main.py to verify database connectivity
- [x] T049 [P] Update backend/README.md with API endpoint documentation and examples
- [x] T050 Create backend/.env.example with example values and comments
- [X] T051 Run quickstart.md validation by following setup steps and testing all 6 endpoints

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (but uses Task model from US1)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories (uses Task model from US1)
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories (uses Task model from US1)
- **User Story 5 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (uses Task model from US1)
- **User Story 6 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories (uses Task model from US1)

**Note**: All user stories depend on the Task model created in US1 (T020). In practice, complete US1 first to establish the model, then other stories can proceed in parallel.

### Within Each User Story

- Models before repositories
- Repositories before services
- Services before routers
- Router before registration in main.py

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002-T005)
- Within Foundational, tasks T008-T011 can run in parallel
- Once US1 completes T020-T021 (models/schemas), other user stories can implement their repositories in parallel
- All Polish tasks marked [P] can run in parallel (T045-T049)

---

## Parallel Example: After Foundational Complete

Once Phase 2 (Foundational) is done and US1 creates the Task model (T020-T021):

```bash
# All user stories can work on their repositories in parallel:
# Team Member A: User Story 1 (list tasks)
# Team Member B: User Story 2 (create task)
# Team Member C: User Story 5 (mark complete)

# Each works independently on their repository/service/router layers
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 5 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T019) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 - View Tasks (T020-T027)
4. Complete Phase 4: User Story 2 - Create Task (T028-T031)
5. Complete Phase 7: User Story 5 - Mark Complete (T039-T041)
6. **STOP and VALIDATE**: Test all 3 P1 stories independently
7. Deploy/demo if ready

**MVP Scope**: 3 user stories (view, create, mark complete) = 35 tasks

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (19 tasks)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP = view only, 8 tasks)
3. Add User Story 2 → Test independently → Deploy/Demo (MVP = view + create, 4 tasks)
4. Add User Story 5 → Test independently → Deploy/Demo (MVP = core 3 features, 3 tasks)
5. Add User Story 3 → Test independently → Deploy/Demo (view single task, 3 tasks)
6. Add User Story 4 → Test independently → Deploy/Demo (update task, 4 tasks)
7. Add User Story 6 → Test independently → Deploy/Demo (delete task, 3 tasks)
8. Polish → Final release (7 tasks)

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (19 tasks)
2. Developer A implements US1 Task model and schemas (T020-T021)
3. Once T020-T021 complete, work splits:
   - Developer A: Finishes US1 (T022-T027)
   - Developer B: Starts US2 using Task model (T028-T031)
   - Developer C: Starts US5 using Task model (T039-T041)
4. Stories complete and integrate independently

---

## Task Count Summary

- **Setup**: 5 tasks
- **Foundational**: 14 tasks
- **User Story 1 (P1)**: 8 tasks
- **User Story 2 (P1)**: 4 tasks
- **User Story 3 (P2)**: 3 tasks
- **User Story 4 (P2)**: 4 tasks
- **User Story 5 (P1)**: 3 tasks
- **User Story 6 (P3)**: 3 tasks
- **Polish**: 7 tasks

**Total**: 51 tasks

**MVP Scope**: 19 (Setup + Foundational) + 8 (US1) + 4 (US2) + 3 (US5) = **34 tasks for MVP**

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
- JWT dependency (T008) is critical - must complete before any router work
