# Repository Layer Rules

## Responsibility

Repositories mediate between services and persistence. They encapsulate data access logic only.

## Required Constraints

- Repository depends only on `db: AsyncSession` (or sync `Session` in sync stacks).
- No business rules and no HTTP concerns.
- Never call `commit` or `rollback`.
- `create` and `update` should `flush` and `refresh`.
- `delete` should `flush` after deletion.
- `update` accepts a Pydantic update schema and applies `model_dump(exclude_unset=True)`.

## CRUD Contract

- `get(pk) -> Model | None`
- `create(obj_in: CreateSchema) -> Model`
- `update(db_obj: Model, obj_in: UpdateSchema) -> Model`
- `delete(pk) -> Model | None`

## Update Method Contract (Mandatory)

Use partial-update semantics exactly:

1. `update_data = obj_in.model_dump(exclude_unset=True)`
2. Iterate fields and apply with `setattr(db_obj, key, value)`
3. `add` + `flush` + `refresh`
4. Return updated ORM model

### Canonical Pattern

```python
async def update(self, *, db_obj: Wallet, obj_in: WalletUpdate) -> Wallet:
    update_data = obj_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obj, key, value)
    self.db.add(db_obj)
    await self.db.flush()
    await self.db.refresh(db_obj)
    return db_obj
```

### Why `exclude_unset=True`

- Prevents accidentally overwriting existing DB values for fields omitted by caller.
- Preserves patch semantics for `Update` DTOs.

### Interaction With `Field(exclude=True)`

If an update DTO marks fields with `Field(exclude=True)`, those fields are intentionally omitted from generic repository update and must be handled explicitly in service logic.

Example use cases:
- API keys written via provider-level repository methods
- nested/special payloads that require validation or fan-out writes

### Good

```python
class LLMSettingsUpdate(BaseModel):
    context_window: int | None = None
    api_key: str | None = Field(default=None, exclude=True)
```

### Bad

```python
class LLMSettingsUpdate(BaseModel):
    context_window: int | None = None
    api_key: str | None = None   # bad: generic update may write sensitive field unexpectedly
```

## Concurrency

For read-modify-write flows, provide locking query methods (`with_for_update`) in the repository.

## Anti-Patterns (Do Not Do)

```python
await self.db.commit()     # bad: transaction boundary violation
```

```python
if obj_in.status == "active":  # bad: business rule in repository
    ...
```

## Standard Pattern

```python
def update(self, *, db_obj: Wallet, obj_in: WalletUpdate) -> Wallet:
    update_data = obj_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obj, key, value)
    self.db.add(db_obj)
    self.db.flush()
    self.db.refresh(db_obj)
    return db_obj
```
