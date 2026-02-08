"""
Load settings from environment. No secrets in code — everything comes from .env.
"""
import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All config from env vars. See .env.example for names."""

    rtsp_url: str = "rtsp://localhost:554/stream1"
    database_url: str = "postgresql://localhost/chattypaws"

    class Config:
        env_file = Path(__file__).resolve().parent.parent / ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


def get_settings() -> Settings:
    return Settings()
