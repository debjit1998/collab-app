from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app import db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await db.init_pool()
    try:
        yield
    finally:
        await db.close_pool()


app = FastAPI(title="Collab API", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/db")
async def health_db() -> dict[str, object]:
    if not db.is_ready():
        raise HTTPException(status_code=503, detail="DATABASE_URL not configured")
    async with db.acquire() as conn:
        cur = await conn.execute("SELECT 1 AS ok")
        row = await cur.fetchone()
    return {"db": "up", "result": row}
