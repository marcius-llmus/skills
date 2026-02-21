# Testing Rules by Layer

## Scope

Use this reference for all test creation/refactors under `tests/`.

## Directory and Fixture Structure

Required project structure:
- Tests grouped by module (`tests/chat/`, `tests/settings/`, `tests/llms/`, etc.).
- Each module owns `fixtures.py`.
- Root `tests/conftest.py` aggregates module fixtures via `pytest_plugins`.

### Good

```python
pytest_plugins = [
    "tests.projects.fixtures",
    "tests.sessions.fixtures",
    "tests.settings.fixtures",
]
```

### Bad

```python
# scattered ad-hoc imports in individual tests
from tests.projects.fixtures import *   # bad
```

## Mandatory Mocking Matrix

1. Router tests mock services.
2. Service tests mock repositories.
3. Repository tests use real DB interactions (no DB mocking).

This is mandatory and non-optional for standard tests.

## Router Tests

### Good

- Use `TestClient`.
- Override DI providers (`app.dependency_overrides`).
- Assert HTTP status/body/headers and service calls.

```python
def test_clear_chat(client, override_get_chat_service, chat_service_mock):
    response = client.post("/chat/clear", headers={"HX-Request": "true"})
    assert response.status_code == 200
    chat_service_mock.clear_session_messages.assert_awaited_once()
```

### Bad

- Calling route handlers directly for endpoint behavior coverage:

```python
response = await cancel_turn.__wrapped__(...)   # bad for route behavior tests
```

Direct invocation is only acceptable for narrow unit tests of pure helper behavior, not route integration behavior.

## Service Tests

### Good

- Instantiate real service with mocked repositories/services.
- Validate business rules, DTO shaping, and downstream calls.

```python
message_repository_mock.create = AsyncMock()
await chat_service.add_user_message(content="hi", session_id=1, turn_id="t1")
message_repository_mock.create.assert_awaited_once()
```

### Bad

```python
# service test hitting real DB for repository behavior
await real_repo.create(...)   # bad: belongs to repository tests
```

## Repository Tests

### Good

- Use real `db_session` fixture (test DB).
- Create rows, flush, query, verify persistence and SQL behavior.

```python
db_session.add(LLMSettings(...))
await db_session.flush()
result = await llm_settings_repository.get_by_model_name("gpt-4.1-mini")
assert result is not None
```

### Bad

```python
llm_settings_repository.get_by_model_name = AsyncMock(...)  # bad in repository tests
```

## DB Fixture Rules

- Keep an isolated DB transaction/session per test function.
- Roll back at end of test to avoid state leakage.
- Enable sqlite FK pragmas in test setup when using sqlite.

## Assertion Quality Rules

- Assert behavior, not implementation trivia.
- For routers: status code + payload/fragment + relevant headers (`HX-Trigger`, `HX-Redirect`).
- For services: domain output + called dependencies.
- For repositories: query semantics, ordering, filtering, and persistence effects.
