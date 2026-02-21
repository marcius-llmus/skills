# Exceptions and Enums Rules

## Exceptions

- Each application defines domain exceptions in its own `exceptions.py`.
- Prefer an app-level base exception (`WalletException`) and specific subclasses.
- Services raise domain exceptions.
- Routes translate domain exceptions to HTTP exceptions.
- Non-HTTP contexts (tasks, workers, scripts) handle domain exceptions contextually (log/retry/fail).

## Enums

- Domain-specific enums live in each app's `enums.py`.
- Cross-cutting enums may live in `app/commons/enums.py`.
- Use `StrEnum` for string-valued enums.
- Reuse enums in both ORM models and Pydantic schemas where appropriate.
