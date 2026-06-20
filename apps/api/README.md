# Collab API

FastAPI backend for the Collab watch-party app. Postgres + Redis via Docker.

## Quick start (local dev)

Spins up Postgres, Redis, and the API with live reload:

```bash
cd apps/api
docker compose -f docker-compose.dev.yml up
```

Wait for `Application startup complete`, then:

```bash
curl localhost:8000/health        # {"status":"ok"}
curl localhost:8000/health/db     # {"db":"up","result":{"ok":1}}
```

Open a `psql` shell to the local DB:

```bash
psql -h localhost -U collab -d collab   # password: collab
```

## Running migrations

Alembic with raw SQL (no ORM, no autogenerate).

```bash
# Apply all pending migrations
docker compose -f docker-compose.dev.yml exec api alembic upgrade head

# Create a new migration (writes to alembic/versions/)
docker compose -f docker-compose.dev.yml exec api alembic revision -m "add foo table"

# Revert the most recent migration
docker compose -f docker-compose.dev.yml exec api alembic downgrade -1
```

Migration files in `alembic/versions/` use raw `op.execute("CREATE TABLE ...")` — no SQLAlchemy models needed.

## Tests + lint

Outside Docker (faster iteration), with a venv:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

ruff check .
ruff format --check .
pytest -q                                 # /health/db is skipped if DATABASE_URL is unset
```

## Production deploy

GitHub Actions builds the image, pushes to ECR, and runs the deploy on the EC2 via SSM:

1. `docker compose pull` (refresh `:latest`)
2. `docker compose run --rm --no-deps api alembic upgrade head` (migrations)
3. `docker compose up -d` (recreates api; redis stays running)

`DATABASE_URL` is fetched from SSM Parameter Store on the EC2 itself — it never appears in CI logs or GitHub secrets. See `.github/workflows/api-deploy.yml`.
