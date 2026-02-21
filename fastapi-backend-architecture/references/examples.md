# Examples

## Route to Service to Repository Update Flow

1. Route validates `WalletUpdate` DTO.
2. Route calls `WalletService.update_wallet(wallet_id, wallet_in)`.
3. Service fetches ORM object from repository and applies business rules.
4. Service passes `(db_obj, wallet_in)` to repository update.
5. Repository uses `model_dump(exclude_unset=True)` + `setattr`, then `flush`/`refresh`.
6. Service converts updated ORM object to `WalletRead` DTO.
7. Route returns DTO and maps domain exceptions to HTTP status codes.

## Inter-Service Call

Consumer service imports provider service's DTO and constructs it explicitly:

```python
wallet_in = WalletCreate(currency="USD", balance=0)
wallet = wallet_service.create_wallet_for_user(user_id=user.id, wallet_in=wallet_in)
```

## Cross-Module Isolation Example

### Good

```python
class SettingsService:
    async def update_settings(self, settings_in: SettingsUpdate) -> SettingsRead:
        if settings_in.coding_llm_settings:
            await self.llm_service.update_coding_llm(...)
        updated = await self.settings_repo.update(db_obj=db_obj, obj_in=settings_in)
        return SettingsRead.model_validate(updated)
```

### Bad

```python
class SettingsService:
    async def _to_public_llm_settings(self, llm_settings):
        return await self.llm_service.llm_settings_repo.get_api_key_for_provider(...)  # bad
```

## Non-HTTP Context

Background task calls service methods and handles domain exceptions without `HTTPException`:

```python
try:
    wallet_service.archive_wallet(wallet_id=wallet_id)
except WalletNotFoundException:
    logger.warning("wallet not found", extra={"wallet_id": str(wallet_id)})
```

## Test Layering Examples

### Router Test (Good)

```python
def test_update_settings(client, override_get_settings_service, settings_service_mock):
    response = client.post("/settings/", headers={"HX-Request": "true"}, json={...})
    assert response.status_code == 204
    settings_service_mock.update_settings.assert_awaited_once()
```

### Service Test (Good)

```python
settings_repo_mock.update = AsyncMock(return_value=settings_obj)
result = await settings_service.update_settings(settings_in=settings_update)
assert result.id == settings_obj.id
settings_repo_mock.update.assert_awaited_once()
```

### Repository Test (Good)

```python
db_session.add(LLMSettings(...))
await db_session.flush()
result = await llm_settings_repository.get_by_model_name("gpt-4.1-mini")
assert result is not None
```
