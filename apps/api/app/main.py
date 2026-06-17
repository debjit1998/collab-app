from fastapi import FastAPI

app = FastAPI(title="Collab API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
