# Chattypaws

Cat “talking button” interpreter: Tapo cameras watch your FluentPet-style buttons, detect presses, log events, and notify you (and your family) on your phones—with optional sound responses. Later: which cat pressed, then meow + body language.

## Plan and stages

**[Staged project plan →](docs/PROJECT_PLAN.md)** — Start there. The plan is:

1. **Stage 1** — Camera (RTSP) + button press detection + PostgreSQL  
2. **Stage 2** — PWA to map buttons in the video to labels  
3. **Stage 3** — Push notifications to iPhone and Android (via PWA)  
4. **Stage 4** — Respond with sound (button sounds or TTS)  
5. **Stage 5** — Which cat pressed (optional)  
6. **Stage 6** — Meow + body language (future)  
7. **Stage 7** — LLM summaries and automation  
8. **Stage 8** — Native apps + Apple Watch  

## Hardware

- **Button-area camera:** **Tapo C120** (wired, RTSP/ONVIF). Used for real-time stream and button-press detection.  
- **Existing:** Tapo TC85 (battery; no RTSP)—general use; not used for the detection pipeline.

## Tech (current)

- **Detection:** Python, OpenCV, Tapo RTSP  
- **Backend:** FastAPI, PostgreSQL  
- **Frontend:** React PWA (Vite), web push  
- **Run:** Raspberry Pi or dev machine for detector; same backend for PWA and (later) native apps  

## How we build

Code is written so that **every step is understandable**: clear names, short comments where needed, and explanations when we add new pieces. If anything is unclear as we go, we can pause and spell it out.

## Next steps

1. Confirm Tapo C120 is on the network and RTSP works (e.g. VLC with `rtsp://<ip>:554/stream1`).  
2. Implement Stage 1 (see [PROJECT_PLAN.md](docs/PROJECT_PLAN.md)).  
3. Add repo layout: `backend/`, `pwa/`, `docs/`.
