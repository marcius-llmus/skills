# Routes Layer Rules

## Responsibility

Routes are the HTTP translation layer. A route should:
1. parse path/query/body inputs
2. rely on FastAPI/Pydantic validation
3. resolve one service dependency
4. call service with primitives and validated schema objects
5. map domain exceptions to `HTTPException`
6. return DTOs (or HTMX context dicts built from DTO/primitives)

## Do

- Keep handlers thin and orchestration-free.
- Depend on service provider functions from `dependencies.py`.
- Use `response_model` for output shape control.
- Translate domain exceptions explicitly.
- For HTMX endpoints, follow [htmx.md](htmx.md).

## Do Not

- Do not implement business rules in routes.
- Do not access the db session directly in routes.
- Do not import repositories in routes.
- Do not raise domain exceptions from routes.
- Do not perform template data orchestration that belongs in page services.

## Standard Pattern

```python
@router.put("/{wallet_id}", response_model=WalletRead)
async def update_wallet(
    wallet_id: UUID,
    wallet_in: WalletUpdate,
    service: WalletService = Depends(get_wallet_service),
):
    try:
        return await service.update_wallet(wallet_id=wallet_id, wallet_in=wallet_in)
    except WalletNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
```
