# Database Setup Rules

## Scope

Use this reference whenever creating or changing:
- DB engine/session setup
- `get_db` dependencies
- transaction boundaries
- repository write behavior
- startup initialization that touches DB

## Canonical Setup (Use This Pattern)

Use the standalone setup script as your baseline implementation:

- [../scripts/database_setup.py](../scripts/database_setup.py)

This script provides:
- async engine + sessionmaker setup
- transactional session context manager
- `Base` declarative model base
- `get_db` dependency template

## Transaction Boundary Contract

- Commit/rollback occurs at request/job dependency boundary (`get_db` / session manager context).
- Services are transaction-unaware.
- Repositories are transaction-unaware.
- Repositories use `flush()`/`refresh()` to persist and hydrate data inside the active transaction.

## Repository Write Contract

### Good

```python
async def create(self, obj_in: EntityCreate) -> Entity:
    db_obj = self.model(**obj_in.model_dump())
    self.db.add(db_obj)
    await self.db.flush()
    await self.db.refresh(db_obj)
    return db_obj
```

### Bad (Do Not Do This)

```python
async def create(self, obj_in: EntityCreate) -> Entity:
    db_obj = self.model(**obj_in.model_dump())
    self.db.add(db_obj)
    await self.db.commit()     # bad: repository controls transaction
    await self.db.refresh(db_obj)
    return db_obj
```

## Service Contract Around DB

### Good

```python
class EntityService:
    async def update(self, *, entity_id: int, entity_in: EntityUpdate) -> EntityRead:
        db_obj = await self.repo.get(entity_id)
        updated = await self.repo.update(db_obj=db_obj, obj_in=entity_in)
        return EntityRead.model_validate(updated)
```

### Bad

```python
class EntityService:
    async def update(self, *, entity_id: int, entity_in: EntityUpdate) -> EntityRead:
        updated = await self.repo.update(...)
        await self.repo.db.commit()   # bad: service controls transaction
        return EntityRead.model_validate(updated)
```

## Startup/Lifespan DB Access

- Startup hooks may run initialization through an async session context.
- Keep initialization logic in services/repositories where possible.
- Avoid bypassing service boundaries for cross-module writes.

## Test DB Expectations

- Repository tests run against real test DB/session fixtures.
- Do not mock repository DB calls in repository tests.
- Use transaction rollback fixture strategy per test function.
