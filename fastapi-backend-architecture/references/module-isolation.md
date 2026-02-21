# Module Isolation and Facade Rules

## Scope

Use this reference whenever code touches more than one module/domain.

## Core Isolation Contract

1. A module must not directly use another module's repository.
2. A module must not mutate another module's state by importing foreign repositories.
3. Cross-module interactions happen through service public methods.
4. For multi-module workflows, use a facade/orchestrator service.

## Allowed Dependency Flow

`ModuleARoute -> ModuleAService -> ModuleARepository`

When Module A needs Module B data/behavior:

`ModuleAService -> ModuleBService`

If multiple module services are coordinated:

`ModuleAFacadeService -> ModuleAService + ModuleBService + ModuleCService`

## Good Patterns

### Service-to-Service

```python
class SettingsService:
    def __init__(self, settings_repo: SettingsRepository, llm_service: LLMService):
        self.settings_repo = settings_repo
        self.llm_service = llm_service

    async def update_settings(self, settings_in: SettingsUpdate) -> SettingsRead:
        if settings_in.coding_llm_settings:
            await self.llm_service.update_coding_llm(
                llm_id=settings_in.coding_llm_settings_id,
                settings_in=settings_in.coding_llm_settings,
            )
```

### Facade/Orchestrator

```python
class PromptSyncFacade:
    def __init__(self, prompt_service: PromptService, project_service: ProjectService):
        self.prompt_service = prompt_service
        self.project_service = project_service

    async def sync_active_project_prompts(self) -> None:
        project = await self.project_service.get_active_project_required()
        await self.prompt_service.sync_for_project(project.id)
```

## Bad Patterns

### Cross-Module Repository Reach-Through

```python
api_key = await self.llm_service.llm_settings_repo.get_api_key_for_provider(...)  # bad
```

```python
await self.prompt_service.prompt_repo.get_project_attachments(...)  # bad
```

These bypass service contracts and increase coupling.

## DTO Boundary in Cross-Module Calls

- Service public methods should consume/return DTOs.
- Avoid passing foreign ORM entities through module boundaries.
- Prefer explicit DTO conversion at service boundary.

## Exception Ownership

- Module-specific exceptions belong to module `exceptions.py`.
- Consumer modules can catch provider module exceptions at service boundary and map as needed.

## Testing Isolation

- In module A service tests, mock module B service (not B repository).
- Verify module A behavior without asserting module B internals.
