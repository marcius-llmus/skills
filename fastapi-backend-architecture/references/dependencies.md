# Dependency Providers Rules

## Core Principle

Transaction lifecycle is centralized in `app/commons/dependencies.py:get_db`.

## `get_db` Contract

- Open session per request.
- Yield session to request scope.
- Commit once when request succeeds and session has changes.
- Roll back on exception.
- Always close session.

## Chained Providers

Each layer component has a provider in application `dependencies.py`:
- repository provider depends on `get_db`
- service provider depends on repository provider (and other service providers if needed)

This enables granular test overrides and clean composition.

## Good Provider Pattern

```python
async def get_entity_repository(
    db: AsyncSession = Depends(get_db),
) -> EntityRepository:
    return EntityRepository(db=db)


async def get_entity_service(
    repo: EntityRepository = Depends(get_entity_repository),
) -> EntityService:
    return EntityService(repository=repo)
```

## Do Not

- Do not perform transaction control in services/repositories/routes.
- Do not instantiate deep dependencies directly inside route functions.

### Bad

```python
@router.post("/")
async def create_entity(db: AsyncSession = Depends(get_db)):
    repo = EntityRepository(db=db)  # bad: wiring in route
    service = EntityService(repo)   # bad: bypasses provider chain
```
