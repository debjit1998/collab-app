# Collab API

FastAPI backend for the Collab watch-party app.

## Local development

```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Then: `curl localhost:8000/health` → `{"status":"ok"}`.

## Tests

```bash
pytest
```

## Lint / format

```bash
ruff check .
ruff format .
```

## Docker

```bash
docker build -t collab-api .
docker run --rm -p 8000:8000 collab-api
```
