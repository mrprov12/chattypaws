# Chattypaws

Cat “talking button” interpreter: Tapo cameras watch your FluentPet-style buttons, detect presses, log events, and notify you (and your family) on your phones and Watch—with optional sound responses. Later: which cat pressed, meow + body language, and an LLM “talking buttons translator” with conversation history.

## Plan and stages

**[Staged project plan →](docs/PROJECT_PLAN.md)** — Start there. Summary:

1. **Stage 1** — Camera (RTSP) + button press detection + PostgreSQL  
2. **Stage 2** — Map buttons in video to labels (config UI or PWA)  
3. **Stage 3** — Home Assistant integration (notifications, desktop, Watch via HA Companion)  
4. **Stage 4** — Respond with sound (button sounds or TTS, e.g. via C120 speaker)  
5. **Stage 5** — Which cat pressed (optional)  
6. **Stage 6** — Meow + body language (future)  
7. **Stage 7** — Talking buttons translator (LLM + conversation history + feedback)  
8. **Stage 8** — Optional native apps + Apple Watch  

## Repo layout

- **`backend-python/`** — FastAPI backend, detector (OpenCV), DB. One backend for PWA, HA add-on, and (later) native apps.  
- **`pwa/`** — React PWA (Vite) for config, mapping, and (optionally) history.  
- **`docs/`** — Project plan and design notes.  
- **`addon/`** (later) — HA add-on packaging (wraps the same backend).

## Versioning (two streams)

We version **backend** and **PWA/apps** separately so each can be released independently. The HA add-on uses the backend version when built.

| Stream              | Where to set version        | When to bump |
|---------------------|-----------------------------|--------------|
| **Backend (+ add-on)** | `backend-python/pyproject.toml` → `[project] version` | API, detector, or server changes. Use this version when building the add-on. |
| **PWA / apps**      | `pwa/package.json` → `version` | UI or client-only changes. |

**How to bump:** Edit the version in the right file (e.g. `0.1.0` → `0.2.0` for a backend feature, or `0.0.1` → `0.0.2` for a PWA fix). Commit with a conventional commit (e.g. `feat(backend-python): add X` or `fix(pwa): Y`). You can add tooling later (standard-version, changesets) to automate bumps and changelogs per stream.

## Hardware

- **Button-area camera:** **Tapo C120** (wired, RTSP/ONVIF, built-in speaker for “respond with sound”).  
- **Existing:** Tapo TC85 (battery; no RTSP)—general use; not used for the detection pipeline.

## Tech (current)

- **Detection:** Python, OpenCV, Tapo RTSP  
- **Backend:** FastAPI, PostgreSQL (SQLite-friendly schema for dev/Pi)  
- **Frontend:** React PWA (Vite); HA first for phone/desktop/Watch, then optional native apps  
- **Run:** Develop on laptop; run backend (and detector) on Pi or dev machine; same backend for PWA, HA add-on, and native clients  

## How we build

Code is written so that **every step is understandable**: clear names, short comments where needed, and explanations when we add new pieces. If anything is unclear as we go, we can pause and spell it out.

## Next steps

1. Confirm Tapo C120 is on the network and RTSP works (e.g. VLC with `rtsp://<ip>:554/stream1`).  
2. Implement Stage 1 (see [PROJECT_PLAN.md](docs/PROJECT_PLAN.md)).  
3. Backend and PWA versions are set in `backend-python/pyproject.toml` and `pwa/package.json`; bump when releasing.
