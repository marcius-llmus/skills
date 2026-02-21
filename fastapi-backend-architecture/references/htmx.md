# HTMX + FastAPI Rules

## Scope

Use this reference whenever implementing or changing:
- HTMX routes/handlers
- partial/full-page template responses
- HX headers (`HX-Trigger`, `HX-Redirect`)
- URL patterns used by HTMX templates

Use this setup/decorator script as baseline:

- [../scripts/htmx_setup.py](../scripts/htmx_setup.py)

## Required Patterns

1. For HTMX-driven views/routes, prefer `@htmx(...)` for rendered endpoints.
2. Return dictionaries from HTMX handlers; let the decorator render templates.
3. Use `Response(status_code=204, headers={...})` for event-style responses without HTML.
4. Keep URLs resource-oriented and consistent with router prefixes.
5. Keep route logic thin; page/service layers assemble template data.

If a view/route uses HTMX, try to use the HTMX decorator unless there is a clear reason not to (for example, highly custom response flow that the decorator cannot represent cleanly).

## URL Conventions

- Collection/list: `GET /{resource}/...`
- Item detail: `GET /{resource}/{id}`
- Item action: `POST|PUT|DELETE /{resource}/{id}/{action}`
- Nested context: `GET /{resource}/{id}/{subresource}`

### Good URL Examples

```text
/projects/
/prompts/project/{prompt_id}/edit
/context/session/{session_id}/file-tree
/projects/{project_id}/activate
```

### Bad URL Examples

```text
/project/{id}                    # singular + inconsistent naming
/prompts/{prompt_id}/edit2       # unclear action naming
/toggle-attachment/{prompt_id}   # action-first URL; not resource-first
```

## Response Patterns

### Good: Partial Rendering

```python
@router.get("/project/{prompt_id}/view", response_class=HTMLResponse)
@htmx("prompts/partials/prompt_item")
async def get_project_prompt_view(...):
    context = await page_service.get_prompt_view_context(prompt_id=prompt_id)
    return context
```

### Good: Event Trigger Without HTML

```python
return Response(
    status_code=status.HTTP_204_NO_CONTENT,
    headers={"HX-Trigger": "settingsSaved"},
)
```

### Good: HTMX Redirect

```python
response = Response(status_code=status.HTTP_200_OK)
response.headers["HX-Redirect"] = f"/sessions/{session.id}"
return response
```

### Bad: HTMLResponse With 204

```python
response = HTMLResponse(status_code=status.HTTP_204_NO_CONTENT)  # avoid
response.headers["HX-Trigger"] = "somethingChanged"
return response
```

Use plain `Response` for 204/no-body cases.

## Template Interaction Rules

- Keep partial templates under `{module}/partials/`.
- Prefer `hx-target` and `hx-swap` to declaratively update UI.
- Use `HX-Trigger` events for cross-component updates.
- Avoid mixing HTMX flows with ad-hoc manual DOM mutation for core behavior.

### Good Template Snippets

```html
<form hx-post="/settings/" hx-target="#settings-form-container" hx-swap="innerHTML">
```

```html
<div hx-get="/projects/" hx-trigger="intersect" hx-swap="innerHTML"></div>
```

### Bad Template Snippet

```html
<button hx-post="/prompts/1/toggle-attachment" onclick="document.getElementById('x').innerHTML=''">
```

Prefer one interaction model for the operation (HTMX + server response), not imperative DOM patching.

## Testing Expectations for HTMX Routes

- Route tests should use `TestClient` with dependency overrides.
- Mock page/domain services; assert status and returned fragment behavior.
- Avoid testing HTMX route behavior via direct `.__wrapped__` handler calls when integration behavior is the test goal.
