# Schemas and Models Rules

## Responsibility Split

- `models.py`: ORM/table definitions.
- `schemas.py`: Pydantic DTOs for create/update/read contracts.

## DTO Contract Rules

- Define explicit DTOs per operation (`EntityCreate`, `EntityUpdate`, `EntityRead`).
- Use update DTOs with optional fields for partial updates.
- Services consume and return these DTOs as stable contracts.
- Route inputs/outputs should be DTO-driven; do not leak ORM models as public contracts.

## Required DTO Set per Entity

- `EntityCreate`: required fields for create
- `EntityUpdate`: optional fields for partial patch
- `EntityRead`: response contract with `model_config = ConfigDict(from_attributes=True)`
- Optional `EntityReadPublic` or `EntityReadBasic` for sanitized/subset projections

### Good

```python
class EntityRead(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)
```

### Bad

```python
class EntityRead(BaseModel):
    __root__: dict   # bad: opaque response contracts
```

## Update DTO Rules (Critical)

Update DTOs define what generic repository updates may mutate.

- Fields handled by dedicated service/repository methods must use `Field(exclude=True)`.
- Keep update DTO fields optional to support partial updates.
- Avoid nested mutable payloads unless service logic explicitly processes them.

### Good

```python
class SettingsUpdate(BaseModel):
    max_history_length: int | None = None
    coding_llm_settings_id: int = Field(exclude=True)
    coding_llm_settings: LLMSettingsUpdate | None = Field(default=None, exclude=True)
```

### Bad

```python
class SettingsUpdate(BaseModel):
    max_history_length: int
    coding_llm_settings: dict | None = None  # bad: required field + untyped nested payload
```

## Circular Import Safety

- Prefer one-way nesting for parent-child read models.
- For reciprocal relations, use local `ReadBasic` models to avoid import cycles.
- Avoid direct model-module circular imports across applications.

## Cross-App Usage

- Construct provider-service DTOs explicitly in consumer services when needed.
- Keep contracts explicit rather than passing untyped dict payloads.

## ORM vs DTO Boundaries

- Repositories return ORM models to services.
- Services convert ORM -> DTO for public service contracts.
- Page services should expose DTO/primitives to templates.
- Do not use ORM types as external API contracts.

## URL/Field Naming Hygiene

- Keep schema field names aligned with domain terms, not transport quirks.
- Do not encode action semantics in entity field names (for example `toggle_*` boolean that represents an action call payload).
