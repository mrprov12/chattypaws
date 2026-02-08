# Backend (Stage 1)

## What's here

- **API** (`main.py`): health check and `GET /events` to list recent button-press events.
- **DB** (`db.py`): PostgreSQL schema (events table) and helpers to insert/list events.
- **Config** (`config.py`): Reads `.env` from repo root; defines `RTSP_URL`, `DATABASE_URL`, `camera_id`. Button regions from `backend-python/data/button_regions.json`.
- **Detector** (`detector.py`): Stub for init; RTSP + motion detection is added on a separate feature branch.

## Run (from repo root)

1. Copy `.env.example` to `.env` at repo root and set `RTSP_URL` (once the camera is here) and `DATABASE_URL`.
2. Create the DB: `createdb chattypaws` (or your PostgreSQL method).
3. Install deps: `pip install -r backend-python/requirements.txt`
4. Start the API: `cd backend-python && uvicorn main:app --reload`
5. In another terminal, run the detector stub: `cd backend-python && python -m detector` (logs that detection is on a feature branch).

The full detector (RTSP + motion-in-regions → events) is implemented on a separate branch. Check `GET http://localhost:8000/events` to see events once that branch is merged and the detector is running.
