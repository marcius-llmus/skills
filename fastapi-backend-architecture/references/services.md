# Services Layer Rules

## Responsibility

Services contain business logic and orchestration only. They are the only layer allowed to coordinate repositories and other services.

## Required Constraints

- No HTTP/web-layer imports (`fastapi`, `starlette`, `HTTPException`).
- Dependencies are constructor-injected (`__init__`).
- Raise domain exceptions from local `exceptions.py`.
- Services must receive Pydantic DTOs for create/update inputs.
- Services must return Pydantic DTOs from public methods.
- Stay transaction-unaware: never call `commit` or `rollback`.

## Inter-Service Rules

- Service-to-service calls are allowed through public methods only.
- Never import another application's repository directly.
- For complex multi-service workflows, add an orchestrator service to keep dependency flow clear.
- Treat foreign-domain models as read-only; mutate via the authoritative service.

## DTO In/Out Contract

### Good

```python
class WalletService:
    def __init__(self, wallet_repository: WalletRepository):
        self.wallet_repository = wallet_repository

    async def update_wallet(
        self, *, wallet_id: int, wallet_in: WalletUpdate
    ) -> WalletRead:
        db_obj = await self._get_wallet_or_raise(wallet_id)
        updated = await self.wallet_repository.update(db_obj=db_obj, obj_in=wallet_in)
        return WalletRead.model_validate(updated)
```

### Bad

```python
class WalletService:
    async def update_wallet(self, *, wallet_id: int, wallet_in: dict) -> Wallet:
        db_obj = await self.wallet_repository.get(wallet_id)
        return await self.wallet_repository.update(db_obj=db_obj, obj_in=wallet_in)
```

Bad because:
- untyped input (`dict`)
- public method returns ORM model (`Wallet`) instead of DTO

## Page Service Contract

Page services are still services and must keep boundaries clean.

- Return `dict[str, Any]` for templates, but values should be DTOs/primitives only.
- Avoid leaking ORM models into template context.
- Keep formatting/presentation assembly here, not in routes/templates.

## Cross-Module Isolation

- Do not access foreign module repos via reach-through attributes (for example `other_service.some_repo...`).
- If cross-module operation spans multiple services, introduce facade/orchestrator service.

## Standard Pattern

```python
class WalletService:
    def __init__(self, wallet_repository: WalletRepository, current_user: User):
        self.wallet_repository = wallet_repository
        self.current_user = current_user

    def update_wallet(self, *, wallet_id: UUID, wallet_in: WalletUpdate) -> WalletRead:
        db_obj = self.get_wallet_by_id(wallet_id)
        updated = self.wallet_repository.update(db_obj=db_obj, obj_in=wallet_in)
        return WalletRead.model_validate(updated)
```
