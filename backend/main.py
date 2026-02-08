"""
Chattypaws API — health check and (Stage 1) events listing.
Run: uvicorn backend.main:app --reload
"""
from fastapi import FastAPI

app = FastAPI(
    title="Chattypaws",
    description="Cat talking-button interpreter: detect presses, store events, notify.",
)


@app.get("/health")
def health():
    """Simple health check so we know the server is up."""
    return {"status": "ok"}


# Stage 1 will add: GET /events, detector service, DB connection
