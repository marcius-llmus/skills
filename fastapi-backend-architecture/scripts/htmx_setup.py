"""Project-agnostic HTMX decorator/init template for FastAPI."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from functools import wraps

from fastapi import HTTPException, Request
from fastapi.templating import Jinja2Templates

TemplatePath = Jinja2Templates | dict[str, Jinja2Templates]
TemplateName = str
templates_path: TemplatePath | None = None
templates_file_extension: str | None = None


@dataclass
class TemplateFileInfo:
    collection: Jinja2Templates
    file_name: TemplateName


@dataclass
class TemplateSpec:
    collection_name: str
    template_name: TemplateName


class MissingFullPageTemplateError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=400, detail="Resource cannot be accessed directly.")


class MissingHTMXInitError(Exception):
    pass


class InvalidHTMXInitError(Exception):
    pass


def _is_fullpage_request(request: Request) -> bool:
    return (
        "HX-Request" not in request.headers
        or request.headers["HX-Request"].lower() != "true"
    )


def _get_template_name(
    name: TemplateSpec | str, file_extension: str | None
) -> TemplateFileInfo:
    if isinstance(name, TemplateSpec) and isinstance(templates_path, dict):
        if name.collection_name not in templates_path:
            raise InvalidHTMXInitError(
                "HTMX init missing requested template collection."
            )
        collection = templates_path[name.collection_name]
        template_name = name.template_name
    else:
        collection = templates_path  # type: ignore[assignment]
        template_name = name  # type: ignore[assignment]

    ext = file_extension or templates_file_extension or "html"
    return TemplateFileInfo(collection=collection, file_name=f"{template_name}.{ext}")


def htmx(
    partial_template_name: TemplateSpec | TemplateName,
    full_template_name: TemplateSpec | TemplateName | None = None,
    partial_template_constructor: Callable | None = None,
    full_template_constructor: Callable | None = None,
    template_extension: str | None = None,
) -> Callable:
    """Render partial/full templates depending on HX-Request header."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, request: Request, **kwargs):
            fullpage = _is_fullpage_request(request=request)
            request.hx_request = not fullpage  # type: ignore[attr-defined]

            if fullpage and full_template_constructor is not None:
                response = (
                    await full_template_constructor(**kwargs)
                    if inspect.iscoroutinefunction(full_template_constructor)
                    else full_template_constructor(**kwargs)
                )
            elif not fullpage and partial_template_constructor is not None:
                response = (
                    await partial_template_constructor(**kwargs)
                    if inspect.iscoroutinefunction(partial_template_constructor)
                    else partial_template_constructor(**kwargs)
                )
            else:
                response = (
                    await func(*args, request=request, **kwargs)
                    if inspect.iscoroutinefunction(func)
                    else func(*args, request=request, **kwargs)
                )

            if response is None:
                response = {}

            if not isinstance(response, Mapping):
                return response

            selected_template = partial_template_name
            if fullpage:
                if full_template_name is None:
                    raise MissingFullPageTemplateError()
                selected_template = full_template_name

            if templates_path is None:
                raise MissingHTMXInitError(
                    "Call htmx_init(...) before using @htmx(...)."
                )

            template = _get_template_name(
                name=selected_template, file_extension=template_extension
            )
            return template.collection.TemplateResponse(
                request,
                template.file_name,
                {"request": request, **response},
            )

        return wrapper

    return decorator


def htmx_init(templates: TemplatePath, file_extension: str = "html") -> None:
    """Initialize templates used by @htmx decorator."""
    global templates_path, templates_file_extension
    templates_path = templates
    templates_file_extension = file_extension
"""Project-agnostic HTMX decorator/init template for FastAPI."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from functools import wraps

from fastapi import HTTPException, Request
from fastapi.templating import Jinja2Templates

TemplatePath = Jinja2Templates | dict[str, Jinja2Templates]
TemplateName = str
templates_path: TemplatePath | None = None
templates_file_extension: str | None = None


@dataclass
class TemplateFileInfo:
    collection: Jinja2Templates
    file_name: TemplateName


@dataclass
class TemplateSpec:
    collection_name: str
    template_name: TemplateName


class MissingFullPageTemplateError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=400, detail="Resource cannot be accessed directly.")


class MissingHTMXInitError(Exception):
    pass


class InvalidHTMXInitError(Exception):
    pass


def _is_fullpage_request(request: Request) -> bool:
    return (
        "HX-Request" not in request.headers
        or request.headers["HX-Request"].lower() != "true"
    )


def _get_template_name(
    name: TemplateSpec | str, file_extension: str | None
) -> TemplateFileInfo:
    if isinstance(name, TemplateSpec) and isinstance(templates_path, dict):
        if name.collection_name not in templates_path:
            raise InvalidHTMXInitError(
                "HTMX init missing requested template collection."
            )
        collection = templates_path[name.collection_name]
        template_name = name.template_name
    else:
        collection = templates_path  # type: ignore[assignment]
        template_name = name  # type: ignore[assignment]

    ext = file_extension or templates_file_extension or "html"
    return TemplateFileInfo(collection=collection, file_name=f"{template_name}.{ext}")


def htmx(
    partial_template_name: TemplateSpec | TemplateName,
    full_template_name: TemplateSpec | TemplateName | None = None,
    partial_template_constructor: Callable | None = None,
    full_template_constructor: Callable | None = None,
    template_extension: str | None = None,
) -> Callable:
    """Render partial/full templates depending on HX-Request header."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, request: Request, **kwargs):
            fullpage = _is_fullpage_request(request=request)
            request.hx_request = not fullpage  # type: ignore[attr-defined]

            if fullpage and full_template_constructor is not None:
                response = (
                    await full_template_constructor(**kwargs)
                    if inspect.iscoroutinefunction(full_template_constructor)
                    else full_template_constructor(**kwargs)
                )
            elif not fullpage and partial_template_constructor is not None:
                response = (
                    await partial_template_constructor(**kwargs)
                    if inspect.iscoroutinefunction(partial_template_constructor)
                    else partial_template_constructor(**kwargs)
                )
            else:
                response = (
                    await func(*args, request=request, **kwargs)
                    if inspect.iscoroutinefunction(func)
                    else func(*args, request=request, **kwargs)
                )

            if response is None:
                response = {}

            if not isinstance(response, Mapping):
                return response

            selected_template = partial_template_name
            if fullpage:
                if full_template_name is None:
                    raise MissingFullPageTemplateError()
                selected_template = full_template_name

            if templates_path is None:
                raise MissingHTMXInitError(
                    "Call htmx_init(...) before using @htmx(...)."
                )

            template = _get_template_name(
                name=selected_template, file_extension=template_extension
            )
            return template.collection.TemplateResponse(
                request,
                template.file_name,
                {"request": request, **response},
            )

        return wrapper

    return decorator


def htmx_init(templates: TemplatePath, file_extension: str = "html") -> None:
    """Initialize templates used by @htmx decorator."""
    global templates_path, templates_file_extension
    templates_path = templates
    templates_file_extension = file_extension
