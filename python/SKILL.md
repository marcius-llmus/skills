---
name: python
description: Generate clean, secure, maintainable Python code. Use when the user asks for Python implementation, refactoring, bug fixes, typing improvements, error handling, architecture guidance, or PEP 8 cleanup.
---

# Python

## Instructions
- Prioritize correctness first, then readability, maintainability, and performance.
- Keep responses concise and direct; provide code-first answers when implementation is requested.
- Use modern Python patterns with explicit types, small focused functions, and clear module boundaries.
- Default to secure behavior: validate inputs, fail safely, and avoid leaking sensitive data in logs or errors.

## Coding Standards
- Follow PEP 8 and keep formatting consistent with the repository's established style.
- Add type hints for public functions, methods, and complex internal interfaces.
- Handle errors intentionally: raise specific exceptions, add contextual messages, and avoid silent failures.
- Prefer concise docstrings for public modules, classes, and functions over excessive inline comments.
- Keep inline comments rare and only for non-obvious logic or trade-offs.
- Avoid `getattr()` and `hasattr()` in normal code paths; prefer explicit attribute access and clear interfaces. Use dynamic attribute access only when truly required by framework/plugin boundaries and isolate it behind a small, well-documented adapter.
- Avoid direct use of `__annotations__` in newly generated code; prefer explicit typing constructs and standard typing/introspection utilities. Do not require cleanup of existing project code unless the user asks for that refactor.

## Architecture Guidance
- Separate business logic from I/O concerns (HTTP, CLI, DB, filesystem, network, external services).
- Keep modules cohesive and APIs explicit; avoid broad utility modules with mixed responsibilities.
- Design for testability: inject dependencies at boundaries and keep pure logic easy to unit test.
- Favor simple abstractions and incremental refactors over introducing new patterns by default.

## Response Style
- Be direct and succinct; avoid unnecessary narration.
- Explain trade-offs only when they affect correctness, maintainability, security, or significant complexity.
- When multiple valid options exist, provide a sensible default first, then brief alternatives.

## Integration with Existing Codebase
- Follow existing project conventions, structure, naming, and tooling over generic preferences.
- Do not introduce new architectural patterns unless requested or clearly justified by the current codebase.
- Preserve backwards compatibility unless the user requests breaking changes.
