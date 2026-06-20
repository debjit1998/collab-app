import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from psycopg import AsyncConnection
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


def _normalize_url(raw: str) -> str:
    # SSM stores the URL in SQLAlchemy form ("postgresql+psycopg://...").
    # psycopg itself wants plain "postgresql://...".
    return raw.replace("postgresql+psycopg://", "postgresql://", 1)


pool: AsyncConnectionPool | None = None


async def init_pool() -> None:
    global pool
    raw = os.environ.get("DATABASE_URL")
    if not raw:
        return
    pool = AsyncConnectionPool(_normalize_url(raw), min_size=1, max_size=10, open=False)
    await pool.open()


async def close_pool() -> None:
    global pool
    if pool is not None:
        await pool.close()
        pool = None


def is_ready() -> bool:
    return pool is not None


@asynccontextmanager
async def acquire() -> AsyncIterator[AsyncConnection]:
    if pool is None:
        raise RuntimeError("Database pool not initialized — set DATABASE_URL and restart")
    async with pool.connection() as conn:
        conn.row_factory = dict_row
        yield conn
