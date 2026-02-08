"""
Load settings from environment. No secrets in code — everything comes from .env.
Button regions are loaded from a JSON file (see get_regions).
"""
from pathlib import Path

from pydantic_settings import BaseSettings

# Repo root is parent of backend-python/.
ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """All config from env vars. See .env.example for names."""

    rtsp_url: str = "rtsp://localhost:554/stream1"
    database_url: str = "postgresql://localhost/chattypaws"
    # Camera identifier (e.g. "c120") — stored with each event.
    camera_id: str = "c120"

    class Config:
        env_file = ROOT / ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


def get_settings() -> Settings:
    return Settings()


# --- Button regions (for detector). File format: list of { "id": "1", "x": 100, "y": 200, "w": 80, "h": 80 } in pixels.
REGIONS_FILE = Path(__file__).resolve().parent / "data" / "button_regions.json"


def get_regions() -> list[dict]:
    """
    Load button regions from JSON. Each region: id, x, y, w, h (pixels in frame).
    If the file is missing or empty, returns [] — detector will treat whole frame as one area for Stage 1.
    """
    if not REGIONS_FILE.exists():
        return []
    import json
    try:
        data = json.loads(REGIONS_FILE.read_text())
        return data if isinstance(data, list) else []
    except Exception:
        return []
