"""
PostgreSQL connection and events table.
All DB access goes through this module so we have one place to understand schema and connections.
"""
import logging
from contextlib import contextmanager
from typing import Generator, Optional

import psycopg2
from psycopg2.extras import RealDictCursor

from config import get_settings

logger = logging.getLogger(__name__)

# Schema: one table for Stage 1. We add button_mappings, etc. in later stages.
EVENTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS events (
    id          SERIAL PRIMARY KEY,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    camera_id   TEXT NOT NULL,
    region_id   TEXT,          -- which button region (null = unknown)
    confidence  REAL           -- 0–1 if we add a score later
);
-- So we can query recent events quickly.
CREATE INDEX IF NOT EXISTS idx_events_created_at ON events (created_at DESC);
"""


def init_schema(conn) -> None:
    """
    Create the events table (and index) if they don't exist.
    Safe to call on every startup.
    """
    with conn.cursor() as cur:
        cur.execute(EVENTS_TABLE_SQL)
    conn.commit()
    logger.info("Schema initialized (events table)")


@contextmanager
def get_connection() -> Generator:
    """
    Yield a DB connection. Caller must use it inside the with block.
    Uses DATABASE_URL from config (.env). Opens and closes the connection for you.
    """
    settings = get_settings()
    conn = psycopg2.connect(settings.database_url)
    try:
        yield conn
    finally:
        conn.close()


def insert_event(camera_id: str, region_id: Optional[str] = None, confidence: Optional[float] = None) -> int:
    """
    Insert one button-press event. Returns the new row id.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO events (camera_id, region_id, confidence)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (camera_id, region_id, confidence),
            )
            row = cur.fetchone()
            conn.commit()
            return row[0]


def list_events(limit: int = 50) -> list[dict]:
    """
    Return the most recent events (newest first). Each row as a dict with id, created_at, camera_id, region_id, confidence.
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, created_at, camera_id, region_id, confidence
                FROM events
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            return [dict(row) for row in cur.fetchall()]
