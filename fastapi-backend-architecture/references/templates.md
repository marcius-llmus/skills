# Templates

## Service Skeleton

```python
class EntityService:
    def __init__(self, repository: EntityRepository):
        self.repository = repository

    async def create(self, *, entity_in: EntityCreate) -> EntityRead:
        db_obj = await self.repository.create(obj_in=entity_in)
        return EntityRead.model_validate(db_obj)
```

## Repository Skeleton

```python
class EntityRepository(BaseRepository):
    async def get(self, pk: UUID) -> Entity | None:
        return await self.db.get(Entity, pk)

    async def create(self, obj_in: EntityCreate) -> Entity:
        db_obj = Entity(**obj_in.model_dump())
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, *, db_obj: Entity, obj_in: EntityUpdate) -> Entity:
        update_data = obj_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_obj, key, value)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj
```

## Dependency Providers Skeleton

```python
async def get_entity_repository(db: AsyncSession = Depends(get_db)) -> EntityRepository:
    return EntityRepository(db=db)

async def get_entity_service(
    repository: EntityRepository = Depends(get_entity_repository),
) -> EntityService:
    return EntityService(repository=repository)
```

## Route Skeleton

```python
@router.put("/{entity_id}", response_model=EntityRead)
async def update_entity(
    entity_id: UUID,
    entity_in: EntityUpdate,
    service: EntityService = Depends(get_entity_service),
):
    try:
        return await service.update(entity_id=entity_id, entity_in=entity_in)
    except EntityNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
```
