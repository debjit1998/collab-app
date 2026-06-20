import os

import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_health_basic() -> None:
    # No lifespan needed for the basic check.
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.skipif(
    "DATABASE_URL" not in os.environ,
    reason="DATABASE_URL not set; skipping DB health check (set it in CI)",
)
def test_health_db() -> None:
    # Lifespan runs on context-manager entry, so the pool actually opens.
    with TestClient(app) as client:
        response = client.get("/health/db")
        assert response.status_code == 200
        body = response.json()
        assert body["db"] == "up"
        assert body["result"] == {"ok": 1}
