# Backend (Stage 1)

## What's here

- **API** (`main.py`): health check and `GET /events` to list recent button-press events.
- **DB** (`db.py`): PostgreSQL schema (events table) and helpers to insert/list events.
- **Config** (`config.py`): Reads `.env` from repo root; defines `RTSP_URL`, `DATABASE_URL`, `camera_id`. Button regions from `backend-python/data/button_regions.json`.
- **Detector** (`detector.py`): Connects to the Tapo C120 RTSP stream, detects motion in regions, writes events to the DB.

## Run (from repo root)

1. Copy `.env.example` to `.env` at repo root and set `RTSP_URL` (once the camera is here) and `DATABASE_URL`.
2. Create the DB: `createdb chattypaws` (or your PostgreSQL method).
3. Install deps: `pip install -r backend-python/requirements.txt`
4. Start the API: `cd backend-python && uvicorn main:app --reload`
5. In another terminal, start the detector (after camera is connected): `cd backend-python && python -m detector`

If the camera isn't connected yet, the detector will log that it can't open the stream and retry every 10 seconds. Once the C120 is on the network and `RTSP_URL` is correct, it will start detecting and writing events. Check `GET http://localhost:8000/events` to see stored events.
