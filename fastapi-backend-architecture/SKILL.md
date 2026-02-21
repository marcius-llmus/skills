---
name: fastapi-backend-architecture
description: Enforces a strict FastAPI backend layered architecture with mandatory reference usage, DTO-based service contracts, centralized transactions, isolated modules, and layer-specific testing rules. HTMX guidance is secondary and optional.
---

# FastAPI Backend Architecture

## Purpose

Apply a strict architecture for FastAPI backends where:
- routes translate HTTP input/output only
- services own business logic and orchestration
- repositories own persistence access only
- dependency providers and `get_db` own transaction/session lifecycle
- tests validate each layer with the correct mocking boundary

HTMX is a secondary concern in this skill. When using HTMX in views/routes, read and apply `references/htmx.md`.

## Non-Negotiable Rules

1. Keep dependencies one-way: `route -> service -> repository -> db`.
2. Services and repositories are transaction-unaware (`no commit/rollback`).
3. Services never import `fastapi`, `starlette`, or `HTTPException`.
4. Services raise domain exceptions; routes map them to HTTP exceptions.
5. Cross-module interactions must be service-to-service (or facade/orchestrator), never repository-to-repository.
6. Service methods must receive and return Pydantic DTOs (`DTO in -> DTO out`).
7. Repository tests use real DB interaction; do not mock DB calls in repository tests.
8. HTMX is optional/secondary in this skill; if HTMX is used, follow `references/htmx.md` and prefer the HTMX decorator pattern.

## Mandatory Reference Invocation Protocol

Before proposing or editing code, required references MUST be called/read first.

If required references are not called, stop and call them before continuing.

Start every task by reading the structural map: [STRUCTURE.md](STRUCTURE.md). This is mandatory.

### Invocation Checklist

1. Read [STRUCTURE.md](STRUCTURE.md) first.
2. Identify target layer(s) and behavior being changed.
3. Call required reference documents from the matrix below.
4. State which references are being applied before proposing code.
5. Apply constraints exactly as written in those references.
6. If implementation conflicts with references, explicitly resolve conflict (do not silently bypass).

### Required Reference Matrix (FastAPI-first)

- **Routes / URL design (primary)**
  - [references/routes.md](references/routes.md)
  - [references/htmx.md](references/htmx.md) (secondary; recommended when HTMX handlers/templates/HX headers are touched)
- **Services / orchestration / cross-module calls**
  - [references/services.md](references/services.md)
  - [references/module-isolation.md](references/module-isolation.md) (required when touching more than one module)
- **Repositories / query methods / update methods**
  - [references/repositories.md](references/repositories.md)
  - [references/database-setup.md](references/database-setup.md) (required when transaction behavior is relevant)
- **Schemas / DTO contracts / update payloads**
  - [references/schemas-models.md](references/schemas-models.md)
  - [references/repositories.md](references/repositories.md) (required for update semantics)
- **Dependency wiring / providers / transaction boundaries**
  - [references/dependencies.md](references/dependencies.md)
  - [references/database-setup.md](references/database-setup.md)
- **Exceptions / enums**
  - [references/exceptions-enums.md](references/exceptions-enums.md)
- **Tests**
  - [references/testing.md](references/testing.md)
  - plus layer reference under test ([references/routes.md](references/routes.md), [references/services.md](references/services.md), or [references/repositories.md](references/repositories.md))
- **Starter scaffolds / implementation examples**
  - [references/templates.md](references/templates.md)
  - [references/examples.md](references/examples.md)
  - [scripts/database_setup.py](scripts/database_setup.py) (DB setup baseline)
  - [scripts/htmx_setup.py](scripts/htmx_setup.py) (HTMX decorator/init baseline)

## Output Expectations

When proposing or editing code with this skill:
- preserve strict layer boundaries
- use explicit typed method signatures and DTO contracts
- keep business logic in services, not routes/repositories/templates
- keep transaction control in `get_db` / session manager boundary
- apply test layering conventions (router mocks service, service mocks repo, repo uses real DB)
- prioritize FastAPI backend guidance first; apply HTMX guidance only when relevant
- include concise rationale when structural decisions are made
