"""
Chattypaws API — health check and (Stage 1) events listing.
Run from backend-python: uvicorn main:app --reload (or from repo root: cd backend-python && uvicorn main:app --reload).
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run on startup: ensure DB schema exists. On shutdown: nothing for now."""
    conn = None
    try:
        with db.get_connection() as conn:
            db.init_schema(conn)
    except Exception as e:
        # So we don't block startup if Postgres isn't up yet (e.g. first run).
        print(f"DB init warning: {e}")
    yield


app = FastAPI(
    title="Chattypaws",
    description="Cat talking-button interpreter: detect presses, store events, notify.",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    """Simple health check so we know the server is up."""
    return {"status": "ok"}


@app.get("/events")
def list_events(limit: int = 50):
    """
    List recent button-press events (newest first).
    Use this to confirm the detector is writing to the DB once the camera is connected.
    """
    return db.list_events(limit=min(limit, 100))
