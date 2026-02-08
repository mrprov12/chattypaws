# Chattypaws — Staged Project Plan

A cat “talking button” interpretation system: Tapo cameras watch FluentPet-style buttons, detect presses, notify you (and your household) on phones and Watch, and optionally respond with sound. Events are stored as a **history**; later stages add which cat pressed, meow + body language, and an **LLM “talking buttons translator”** that interprets button sequences (and optional feedback on what the cat wanted) with conversation history over time.

**Your setup:** Tapo C120 camera(s), FluentPet-style buttons (record-your-voice, no Bluetooth hub), Raspberry Pi available. Develop on laptop first; document and support running on Pi. **Home Assistant first** for phone, desktop, and Apple Watch (via HA Companion app); a later optional stage can add dedicated iPhone/Android apps, Apple Watch app, and desktop app if desired. **Hardware note:** C120 has built-in speaker and two-way audio (playback via go2rtc/ffmpeg or HA; fallback Pi or smart speaker if needed).

---

## Design principles

- **Stage by stage:** Each stage is shippable and useful on its own.
- **Laptop then Pi:** Develop and debug on laptop; document deployment and support for Raspberry Pi. Detection/ingestion can run on either.
- **Home Assistant first:** Phone, desktop, and Watch experience via HA (Companion app + dashboard). One add-on or integration to build and maintain; HA handles notifications, UI, and Watch.
- **Optional native later:** A later stage can add dedicated iOS app, Android app, Apple Watch app, and/or desktop app (same backend). Phone codebase(s) can be one cross-platform app or separate iOS and Android codebases as needed.
- **Database:** Design for PostgreSQL (primary). Use a thin abstraction so SQLite can be swapped in for dev or minimal Pi setup if desired.
- **Tech can change:** We’ll call out where to re-evaluate choices (e.g. LLM, TTS) as we reach those stages.

---

## Stage 1 — Foundation: Camera stream + button press detection + storage

**Goal:** See the camera, detect when a button is pressed, and store each event with a timestamp. No UI or notifications yet.

**Outcomes:**

- Dev machine (or Raspberry Pi) pulls RTSP from one Tapo C120 camera.
- OpenCV (or similar) processes frames and detects “button press” (motion/change in button regions).
- Events saved to PostgreSQL: `timestamp`, `camera_id`, `button_region_id` (or “unknown”), optional `confidence`. This forms the **history** of button presses for later conversation view and translator.
- Minimal script or API to verify: “events are being written.”

**Technical notes:**

- **Event types:** For now the `events` table stores **button presses only**. Feedback, “response played,” and conversation metadata live in other tables or columns (Stage 7). If we later want one unified timeline (e.g. multiple event types in one table), we can add an `event_type` (e.g. `button_press`, `response_played`) and keep a single history; otherwise keep this table for presses and use separate tables for the rest.
- **Who said it (cat_id):** Add in **Stage 5** when we have cat identification. No need to populate it in Stage 1. Optionally add a nullable `cat_id` column to the schema from the start so we don’t need a migration later; otherwise add the column in Stage 5.
- **Tapo C120:** Use RTSP (ensure RTSP/ONVIF is enabled in Tapo app and use a dedicated camera user). Stream URLs typically like `rtsp://<camera_user>:<password>@<ip>:554/stream1`. C120 supports RTSP for video.
- **Detection:** Start with motion/change detection in fixed regions (you’ll define button regions in a later stage). Optionally use a small CNN or existing “object/action” model later if needed.
- **Stack:** Python (FastAPI or Flask) + OpenCV + PostgreSQL. Develop on laptop first; document running on Pi. Postgres can be on the Pi or on a home server/cloud.

**Deliverables:**

- [ ] RTSP connection to at least one Tapo C120 from dev machine (then document for Pi).
- [ ] Config/code that defines one or more “button regions” (e.g. bounding boxes or masks).
- [ ] Detector that outputs “press” events with timestamp and region.
- [ ] PostgreSQL schema (e.g. `events` table) and code that writes events.
- [ ] Simple way to confirm events in DB (CLI or one GET endpoint).

**Risks / mitigations:**

- Button press is subtle (paw touch): we may need to tune sensitivity or use a small ML model; start with motion in region + short “cooldown” to avoid double-counting.

---

## Stage 2 — Button mapping (map buttons in video to labels)

**Goal:** You can point a camera at the buttons and draw or adjust regions on the video and label each region with what the button says (e.g. “food”, “outside”, “play”). Mapping can be done via a minimal UI (e.g. backend-served page or HA dashboard) or a small PWA.

**Outcomes:**

- View of camera (live or snapshot via backend streaming RTSP or serving stills).
- UI to add/move/resize regions and assign a label and optional “sound id” (for later playback).
- Mapping saved to backend/DB and used by the detector so events have a `button_label` (e.g. “food”) not just “region 2”.

**Technical notes:**

- **Video:** Backend exposes a live stream (e.g. MJPEG or HLS) or frequent stills from RTSP. Dev machine or Pi can run GStreamer/FFmpeg to repackage RTSP to browser-friendly format. Same feed can be used in HA or a minimal config UI.
- **Mapping storage:** e.g. `button_mappings` table: `camera_id`, `region` (JSON or separate x,y,w,h), `label`, `sound_id` (optional), `order`.
- **Stack:** Backend from Stage 1 extended with mapping API and stream endpoint; UI can be a minimal web page, small PWA, or HA Lovelace (depending on HA integration timing).

**Deliverables:**

- [ ] View of camera (live or near-live) in config UI or HA.
- [ ] Draw/edit regions and assign labels (and optional sound id).
- [ ] Save/load mappings per camera.
- [ ] Detector updated to attach `button_label` (and `sound_id`) to each event.

**Risks / mitigations:**

- Low latency for “live” mapping: start with 1–2 FPS or MJPEG; optimize later if needed.

---

## Stage 3 — Home Assistant integration (notifications, desktop, Watch)

**Goal:** When a button press is detected, you get a push notification on your phone and Apple Watch, and can see events and respond from the HA dashboard (desktop). All via Home Assistant so one integration/add-on covers phone, desktop, and Watch.

**Outcomes:**

- Button-press events from the detector are exposed to Home Assistant (e.g. via REST API, MQTT, or HA integration). HA sends push notifications to the Companion app (iPhone and Android).
- HA Companion app on Apple Watch receives notifications; you can see “Food — just now” and optionally act (e.g. run a script to respond with sound). Note: actionable notification responses from Watch to HA can be less reliable than from iPhone; document and test.
- HA dashboard (Lovelace) provides desktop view: live or recent events, history, and controls (e.g. “Respond with sound”).

**Technical notes:**

- **Chattypaws as HA add-on or integration:** Detector + backend run as an add-on or alongside HA; they publish events (and optionally entities) to HA. HA handles notification delivery via Companion apps.
- **Flow:** New event → backend notifies HA or pushes to MQTT/API → HA triggers notifications and updates dashboard. Optional: store push subscriptions in our DB for a future non-HA path, or rely entirely on HA.
- **Optional:** Add SMS (e.g. Twilio) or email as fallback; can be a later sub-task.

**Deliverables:**

- [ ] Chattypaws events available in HA (sensors, events, or dashboard).
- [ ] Push notifications to iPhone and Android via HA Companion when a button is pressed.
- [ ] Notification (and Watch) shows button label and timestamp.
- [ ] HA dashboard shows recent events and (when Stage 4 is done) way to respond with sound.
- [ ] Document: add PWA to Home Screen / install Companion for best experience; note Watch actionable limits.

**Risks / mitigations:**

- HA Companion Watch actionable notifications may not always be received by HA; document and test; optional native Watch app in a later stage if reliability is critical.

---

## Stage 4 — Respond with sound (button sounds or TTS)

**Goal:** After a button press, you (or the system) can trigger a sound response: either the same recording as the button or a spoken phrase.

**Outcomes:**

- Option A: Playback of the same sound the button plays (e.g. “food”, “outside”). Requires having those audio files and a way to play them near the cat (e.g. Tapo camera with speaker, or a separate speaker).
- Option B: TTS response (“Okay, coming to feed you!”). Same playback path.
- UI: from HA dashboard or Companion when you see a notification or open the event, tap “Respond with sound” and choose pre-recorded sound or type a phrase for TTS.

**Technical notes:**

- **Tapo C120:** Has built-in speaker and full-duplex two-way audio; playback is supported (e.g. via go2rtc or ffmpeg with Tapo/RTSP; used with HA). Add ~1.2s silence to avoid clipping. If playback is unreliable on your firmware, fallback: Pi-connected speaker or smart speaker.
- **Sound library:** Store recordings for each button label (record or upload via config UI or HA). Table: `sounds` (id, label, file_path or URL).
- **TTS:** Use a cloud TTS (e.g. Google Cloud TTS, ElevenLabs, or open source like Piper/Coqui) or local TTS on Pi; send generated audio to the same playback device.
- **Trigger:** Manual from HA or config UI first; optional “auto-suggest” or “auto-play” in a later stage.

**Deliverables:**

- [ ] Sound library: record or upload one sound per button label; play back for testing (config UI or HA).
- [ ] Playback path to C120 speaker (go2rtc/ffmpeg or HA); document and test. Fallback: Pi or smart speaker.
- [ ] “Respond” action on an event (from HA or config UI) → choose sound or enter text → TTS or sound plays on C120 (or fallback device).
- [ ] (Optional) Quick “Play again” from notification or dashboard.

**Risks / mitigations:**

- C120 two-way audio can be less responsive in some reviews; test and document; fallback remains Pi or smart speaker.

---

## Stage 5 — Which cat pressed (optional multi-cat identification)

**Goal:** When a button is pressed, the system has a best-guess of which cat did it (e.g. “Milo” vs “Luna”), and shows that in the event and in notifications.

**Outcomes:**

- Events have an optional `cat_id` (or “unknown”). Notifications can say “Milo asked for Food.”
- PWA can show history per cat and refine labels (e.g. “That was Luna” correction).

**Technical notes:**

- **Input:** Same camera stream; use a short clip around the press (e.g. 2–5 seconds before/after).
- **Approaches (in order of complexity):**  
  (1) Small CNN or ViT fine-tuned on your cats’ faces/backs (need a few hundred labeled frames per cat).  
  (2) Reuse a pre-trained “pet” or “animal” detector + simple classifier (color/size/pattern) if enough to tell yours apart.  
  (3) Body/pose (skeleton) as a proxy if faces are often not visible.
- **Pipeline:** On button press, extract clip → run classifier → store `cat_id` with event. Allow “correct cat” in PWA to collect training data for future improvement.

**Deliverables:**

- [ ] Dataset: label some past events (or clips) with cat identity.
- [ ] Model or heuristic that outputs cat_id (or “unknown”) for a clip.
- [ ] Pipeline: on each press, run classifier and save cat_id with event.
- [ ] PWA and notifications show “which cat” when available; PWA allows correction and (optionally) retraining.

**Risks / mitigations:**

- Accuracy will be imperfect at first; “unknown” and manual correction keep it useful.

---

## Stage 6 — Meow + body language (future)

**Goal:** Enrich context with meow audio and simple body-language cues, so you get “Milo asked for Food and meowed; he’s at the door” style summaries.

**Outcomes:**

- Optional meow detection (from camera mic or separate mic); optional “meow type” (e.g. demand vs greeting) via a small audio model.
- Optional body-language tags (e.g. “tail up”, “at door”, “sitting”) from pose or simple CNN on same camera.
- Events can store: button press + optional meow + optional body tags; notifications/summaries can combine them.

**Technical notes:**

- **Meow:** Librosa + small classifier (or fine-tuned wav2vec/whisper tiny) for “meow vs silence” and maybe “type”; run on Pi or cloud.
- **Body:** Pose estimation (e.g. OpenPose animal or MediaPipe) or small CNN for a few postures; scope down to 3–5 useful tags.
- **Integration:** Triggered by same event pipeline (clip + audio segment); store as extra fields or related rows. LLM summarization can come in Stage 7.

**Deliverables:**

- [ ] Meow detection (and optionally type) stored with (some) events.
- [ ] Body-language tags (small set) when feasible from video.
- [ ] PWA and notifications show combined context (button + cat + meow + body) where available.

---

## Stage 7 — Talking buttons translator (LLM interpretation + history + automation)

**Goal:** Interpret what is being said from **which cat** pressed **which buttons** (and optional meow/body) via an LLM layer: plain-language “translator” summaries (“Milo is asking for food and wants to play”), a **history of conversations** over time, optional feedback on what the cat wanted, and optional automation.

**Outcomes:**

- **Translator:** LLM takes (cat + button sequence + optional meow/body) and outputs a short interpretation (e.g. “Milo pressed Food, then Play — asking for food and wants to play”). Shown in notifications and in history.
- **Conversation history:** Events are **grouped into conversations** (e.g. same cat, presses within a time window such as 5–10 minutes, or explicit “session”) so you can see “last conversations over time” with each conversation’s interpretation.
- **Feedback:** Option to record what the cat actually wanted after the fact (e.g. “I fed him” / “he wanted the door open”). Stored with the event or conversation; displayed in history (“you said they wanted …”) and available for future tuning of the translator.
- Optional: “Suggest response” (sound or TTS) and one-tap to play; optional rules (e.g. “if ‘outside’ and evening, play ‘Not now’ and notify”).

**Technical notes:**

- **Grouping:** Define “conversation” as a set of events (e.g. same `camera_id`, same `cat_id`, within N minutes of each other). Store `conversation_id` on events or derive via query; optional `conversations` table (id, start_ts, end_ts, cat_id, interpretation, feedback).
- **LLM (translator):** Small local model (e.g. Llama.cpp on Pi) or Hugging Face / OpenAI API. Input: cat + ordered list of button labels (+ optional meow/body). Output: 1–2 sentence interpretation and optional response suggestion. Run per event for live summary, or per conversation for history view.
- **Feedback:** Table or fields for “what the cat wanted” / “what you did” (free text or structured); link to event or conversation. Feeds translator display and, later, optional prompt/feedback loop for optimization.
- **Automation:** Simple rule engine (if event/conversation matches condition → send notification and/or play sound). No need for full home-automation stack initially.

**Deliverables:**

- [ ] LLM interpreter: cat + button sequence (+ meow/body) → plain-language summary (translator); shown in notifications and in app.
- [ ] Conversation grouping: define and store or derive conversations; API or query for “recent conversations.”
- [ ] History view: “last conversations over time” with interpretation (and optional feedback) per conversation; in HA dashboard or config UI.
- [ ] Optional feedback: record “what the cat wanted” / “what you did” per event or conversation; store and display in history.
- [ ] (Optional) Rule-based automation for play sound / notify.
- [ ] (Optional) Optimizations: use feedback and usage to tune prompts or improve interpreter over time.

---

## Stage 8 — Optional native apps and desktop (later)

**Goal:** If desired, dedicated iPhone app, Android app, Apple Watch app, and/or desktop app for quick view and “respond with sound” (e.g. pick a button sound from the Watch). Same backend; HA remains supported.

**Outcomes:**

- Native apps use same backend; better background notifications and Watch integration.
- Watch: receive button-press notification and send back a response from the available buttons (reliable vs HA actionable notifications).
- Desktop: dedicated app or PWA if not using HA dashboard.

**Technical notes:**

- **Phone:** One cross-platform codebase (React Native/Flutter) or separate iOS (Swift/SwiftUI) and Android (Kotlin) codebases.
- **Apple Watch:** Swift/SwiftUI for best experience; last event + quick respond from button list.
- Backend stays the same; HA integration continues to work; native apps are additional clients.

**Deliverables:**

- [ ] (Optional) iOS app and Android app (same backend).
- [ ] (Optional) Apple Watch companion: receive notification, respond with chosen button sound.
- [ ] (Optional) Desktop app or PWA.

---

## Suggested tech stack (current)

| Layer           | Choice              | Notes                                      |
|----------------|---------------------|--------------------------------------------|
| Camera         | Tapo C120 (RTSP)    | RTSP enabled; dedicated user; C120 has speaker for playback |
| Detection      | Python + OpenCV     | Pi or server; add small CNN if needed      |
| Backend        | FastAPI (Python)    | Async, good for streams and push          |
| DB             | PostgreSQL          | Primary; schema allows SQLite swap for dev/Pi |
| Phone/Desktop/Watch | Home Assistant first | Companion app + dashboard; optional PWA or config UI |
| Push           | HA Companion        | Notifications via HA; no Web Push required for HA path |
| Notifications  | HA first            | Optional native apps in Stage 8            |
| Sound playback | Tapo C120 speaker   | go2rtc/ffmpeg or HA; fallback Pi+speaker; TTS via API or Pi |
| Later          | TensorFlow/PyTorch  | Cat ID, meow, body; Hugging Face for LLM   |

---

## Running / deployment (containers)

Yes — the backend (and thus the HA add-on) are intended to run as **containerized** services. Native apps and PWA are clients that talk to the backend; they don’t run “on the server.”

| Piece | How it runs |
|-------|------------------|
| **Backend** | **Docker container** (one image: FastAPI + detector + OpenCV). Runs on your Pi, home server, or cloud. Can use the same image for standalone (“run the backend on my Pi”) or as the base for the HA add-on. Postgres can be in a separate container or on the host. |
| **HA add-on** | **Container** as well — Home Assistant add-ons are Docker-based. The add-on is this backend image plus HA add-on metadata (config.yaml, run script). HA runs the container and manages its lifecycle. |
| **PWA** | Built to static files. Either (a) **served by the backend container** (FastAPI serves the built PWA from `pwa/dist`), or (b) served by a small web server (e.g. nginx) in its own container or on the same host. Simplest: one backend container that serves both the API and the PWA. |
| **Native apps** | Not server-side. They’re installed on phones/Watch/desktop and call the backend API (over your network or a tunnel). No container for “the app”; only the backend is containerized. |

So in practice: you’ll have at least **one Docker image** for the backend (and optionally a Compose setup with backend + Postgres). When you add the HA add-on, that image is repackaged or reused for HA’s add-on format. PWA is either inside that backend image or in a second, small serve container. Re-evaluate when you get to Stage 3 (HA) and document the exact run instructions (e.g. `docker compose up`, or “Install Chattypaws add-on from …”).

**HA add-on vs backend — not “inside” backend-python:** The add-on is **the same backend** (backend-python) plus **add-on packaging**. That packaging lives in a **separate folder** in the repo (e.g. `addon/` or `hassio/`), not inside `backend-python/`. That folder contains: HA add-on config (`config.yaml`), a Dockerfile that builds or uses the backend image, and a run script. So: `backend-python/` = the service; `addon/` = “how to run that service as an HA add-on.” The add-on doesn’t add new application code; it’s just the backend in HA’s add-on format.

**How we build the client/frontend for HA:** We don’t ship a separate “Chattypaws app” for HA. The **client** is Home Assistant itself (Lovelace dashboard, HA Companion app). We only need to expose our data and actions to HA. Two options:

1. **Entities only (no custom UI):** The backend/add-on registers **entities** (sensors, buttons, etc.) and **services** with HA. Users see them in the HA UI and build their own dashboard with **standard Lovelace cards** (entity cards, buttons, etc.). No custom frontend code; we only implement the integration/add-on side that creates entities.
2. **Custom Lovelace / custom integration:** If we want a dedicated Chattypaws panel or cards (e.g. “Conversation history,” “Respond with sound” picker), we build a **custom integration** and/or **custom Lovelace cards** (JavaScript/TypeScript, following [HA’s custom component and frontend API](https://developers.home-assistant.io/docs/frontend)). That code lives in the repo (e.g. `ha-frontend/` or inside the add-on as a custom component) and is loaded by HA. So “HA frontend” = either zero (use standard cards) or a small JS/TS codebase for custom cards/panel.

**Docker is already initialized:** The repo has `backend-python/Dockerfile`, `backend-python/.dockerignore`, and a root `docker-compose.yml` (backend + Postgres) so we can run the stack in containers when needed. See README for how to run with Docker.

---

## Versioning (two streams: backend+add-on vs PWA/apps)

We use **two version streams** so server and client can be released independently. The HA add-on reuses the backend version when built (add-on 1.2.0 = ships backend 1.2.0).

| Stream | What it versions | Where version lives | When to bump |
|--------|------------------|--------------------|--------------|
| **Backend (+ HA add-on)** | Core service (backend-python) and the add-on when packaged for HA. Same version for both. | `backend-python/pyproject.toml` → `[project] version` | API, detector, or server logic changes. When you build the add-on, use this version. |
| **PWA / apps** | PWA and (later) native iOS/Android/Watch/desktop apps. One shared app version or per-platform. | `pwa/package.json` → `version`; each app project when added | UI, app features, client-only fixes. |

- **Compatibility:** Document which PWA/app version works with which backend version (e.g. “App 1.x works with backend 1.x”); use API versioning if needed.
- **Conventional commits:** Scopes drive which stream to bump — `backend-python` (and add-on when present) → backend version; `pwa`, `ios`, `android` → PWA/app version. Bump the relevant version file when releasing; optional tooling (standard-version, changesets, or semantic-release) can be added per stream later. See the repo **README** for where to edit and how to bump.

---

## What we can do next

1. **Lock Stage 1:** Tapo C120 confirmed; develop on laptop, then document for Pi. Implement RTSP → OpenCV → event detection → PostgreSQL (schema allows SQLite for dev).
2. **Repository structure:** `docs/` (this plan), `backend/` (FastAPI + detector + DB), `pwa/` or config UI as needed, optional `scripts/`.
3. **Database schema:** Draft tables for `events`, `button_mappings`, `push_subscriptions`, `sounds` (Postgres-first, SQLite-friendly abstraction). Later stages add conversation grouping and optional `conversations` / feedback fields for the translator and history.
4. **Later:** HA add-on/integration (Stage 3) so phone, desktop, and Watch go through Home Assistant first; optional native apps in Stage 8 if desired.
