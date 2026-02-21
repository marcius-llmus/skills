"""Project-agnostic FastAPI async database setup template."""

from __future__ import annotations

import contextlib
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for ORM models."""


class DatabaseSessionManager:
    """Owns engine/sessionmaker and transaction-scoped async sessions."""

    def __init__(self, database_url: str, engine_kwargs: dict[str, Any] | None = None):
        self._engine = create_async_engine(database_url, **(engine_kwargs or {}))
        self._sessionmaker = async_sessionmaker(self._engine, expire_on_commit=False)

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self._sessionmaker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def close(self) -> None:
        await self._engine.dispose()


# Example: initialize this at app startup from settings/env.
sessionmanager = DatabaseSessionManager(
    database_url="sqlite+aiosqlite:///./app.db",
    engine_kwargs={"echo": False},
)


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding one transactional session per request."""
    async with sessionmanager.session() as session:
        yield session
