# Chattypaws — Staged Project Plan

A cat “talking button” interpretation system: Tapo cameras watch FluentPet-style buttons, detect presses, notify you (and your husband) on your phones, and optionally respond with sound. Later: which cat pressed, then meow + body language.

**Your setup:** Tapo cameras, FluentPet-style buttons (record-your-voice, no Bluetooth hub), Raspberry Pi available, goal of PWA + eventual Apple Watch and native mobile apps.

---

## Design principles

- **Stage by stage:** Each stage is shippable and useful on its own.
- **Raspberry Pi–friendly:** Detection/ingestion can run on the Pi; optional cloud for history/notifications.
- **One codebase for phones first:** PWA with web push reaches both iPhone and Android; native apps come later.
- **Tech can change:** We’ll call out where to re-evaluate choices (e.g. LLM, TTS) as we reach those stages.

---

## Stage 1 — Foundation: Camera stream + button press detection + storage

**Goal:** See the camera, detect when a button is pressed, and store each event with a timestamp. No UI or notifications yet.

**Outcomes:**

- Raspberry Pi (or your dev machine) pulls RTSP from one Tapo camera.
- OpenCV (or similar) processes frames and detects “button press” (motion/change in button regions).
- Events saved to PostgreSQL: `timestamp`, `camera_id`, `button_region_id` (or “unknown”), optional `confidence`.
- Minimal script or API to verify: “events are being written.”

**Technical notes:**

- **Tapo:** Use RTSP (wired Tapo cameras; ensure RTSP/ONVIF is enabled in Tapo app and use a dedicated camera user). Stream URLs typically like `rtsp://<camera_user>:<password>@<ip>:554/stream1`.
- **Detection:** Start with motion/change detection in fixed regions (you’ll define button regions in a later stage). Optionally use a small CNN or existing “object/action” model later if needed.
- **Stack:** Python (FastAPI or Flask) + OpenCV + PostgreSQL. Pi runs the detector service; Postgres can be on the Pi or on a home server/cloud.

**Deliverables:**

- [ ] RTSP connection to at least one Tapo camera from Pi (or dev machine).
- [ ] Config/code that defines one or more “button regions” (e.g. bounding boxes or masks).
- [ ] Detector that outputs “press” events with timestamp and region.
- [ ] PostgreSQL schema (e.g. `events` table) and code that writes events.
- [ ] Simple way to confirm events in DB (CLI or one GET endpoint).

**Risks / mitigations:**

- Button press is subtle (paw touch): we may need to tune sensitivity or use a small ML model; start with motion in region + short “cooldown” to avoid double-counting.

---

## Stage 2 — Button mapping PWA (map buttons in video to labels)

**Goal:** You can point a camera at the buttons and, in a PWA, draw or adjust regions on the video and label each region with what the button says (e.g. “food”, “outside”, “play”).

**Outcomes:**

- PWA that shows live or snapshot from the camera (via your backend streaming the RTSP or serving stills).
- UI to add/move/resize regions and assign a label and optional “sound id” (for later playback).
- Mapping saved to backend/DB and used by the detector so events have a `button_label` (e.g. “food”) not just “region 2”.

**Technical notes:**

- **Video in PWA:** Backend exposes a live stream (e.g. MJPEG or HLS) or frequent stills from RTSP so the PWA doesn’t need to connect to RTSP directly. Pi or server can run GStreamer/FFmpeg to repackage RTSP to browser-friendly format.
- **Mapping storage:** e.g. `button_mappings` table: `camera_id`, `region` (JSON or separate x,y,w,h), `label`, `sound_id` (optional), `order`.
- **Stack:** React (or Vue/Svelte) PWA; backend from Stage 1 extended with mapping API and stream endpoint.

**Deliverables:**

- [ ] PWA (installable, works on phone and desktop).
- [ ] View of camera (live or near-live).
- [ ] Draw/edit regions and assign labels (and optional sound id).
- [ ] Save/load mappings per camera.
- [ ] Detector updated to attach `button_label` (and `sound_id`) to each event.

**Risks / mitigations:**

- Low latency for “live” mapping: start with 1–2 FPS or MJPEG; optimize later if needed.

---

## Stage 3 — Notifications (push to your iPhone and husband’s Android)

**Goal:** When a button press is detected, both of you get a push notification (and optionally SMS or another fallback).

**Outcomes:**

- Push notifications to both phones when an event occurs. Body text includes at least the button label and time (e.g. “Food — just now”).
- PWA is the “app” that receives push: add to Home Screen on iPhone (required for iOS web push), install on Android. One PWA for both.

**Technical notes:**

- **Web Push (VAPID):** Backend sends web push via standard Web Push API. No native apps required. Works on iOS 16.4+ when PWA is added to Home Screen; works on Android in supported browsers.
- **Flow:** User opens PWA → prompts for notification permission → backend stores subscription (e.g. in `push_subscriptions` table). On new event, backend sends one push per subscription (you + husband).
- **Optional:** Add SMS (e.g. Twilio) or email as fallback; can be a later sub-task.

**Deliverables:**

- [ ] PWA requests notification permission and registers push subscription with backend.
- [ ] Backend stores subscriptions and sends web push on new event.
- [ ] Notification payload includes button label and timestamp.
- [ ] Tested on your iPhone (PWA on Home Screen) and husband’s Android.

**Risks / mitigations:**

- iOS only allows web push for Home-Screen-added PWAs; we’ll document that step clearly in the app.

---

## Stage 4 — Respond with sound (button sounds or TTS)

**Goal:** After a button press, you (or the system) can trigger a sound response: either the same recording as the button or a spoken phrase.

**Outcomes:**

- Option A: Playback of the same sound the button plays (e.g. “food”, “outside”). Requires having those audio files and a way to play them near the cat (e.g. Tapo camera with speaker, or a separate speaker).
- Option B: TTS response (“Okay, coming to feed you!”). Same playback path.
- UI in PWA: when you see a notification or open the event, you can tap “Respond with sound” and choose pre-recorded sound or type a phrase for TTS.

**Technical notes:**

- **Tapo cameras:** Some Tapo models have a speaker and support playing sound (e.g. via Tapo API or RTSP/ONVIF if supported). If not, use a smart speaker or a Pi-connected speaker.
- **Sound library:** Store recordings for each button label (you record them once in the PWA or upload files). Table: `sounds` (id, label, file_path or URL).
- **TTS:** Use a cloud TTS (e.g. Google Cloud TTS, ElevenLabs, or open source like Piper/Coqui) or local TTS on Pi; send generated audio to the same playback device.
- **Trigger:** Manual from PWA first; optional “auto-suggest” or “auto-play” in a later stage.

**Deliverables:**

- [ ] Sound library: record or upload one sound per button label; play back from PWA (for testing).
- [ ] Playback path to camera/speaker (document which Tapo model and how: e.g. Tapo app API or local speaker).
- [ ] In PWA: “Respond” action on an event → choose sound or enter text → TTS or sound plays on device.
- [ ] (Optional) Quick “Play again” for the same sound from notification or PWA.

**Risks / mitigations:**

- Tapo may not expose a “play audio” API; fallback: small speaker connected to Pi, or smart speaker with local API.

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

## Stage 7 — Summaries and automation (LLM + optional automation)

**Goal:** Plain-language summaries (“Milo is asking for food and seems eager”) and optional suggested responses or automated playbacks.

**Outcomes:**

- When you open the app or get a notification, you see a short summary (button + cat + meow + body).
- Optional: “Suggest response” (sound or TTS) and one-tap to play.
- Optional: rules (e.g. “if ‘outside’ and time is evening, play ‘Not now’ and notify”).

**Technical notes:**

- **LLM:** Small local model (e.g. Llama.cpp on Pi) or Hugging Face / OpenAI API; prompt: event fields → 1–2 sentence summary and optional response suggestion.
- **Automation:** Simple rule engine (if event matches condition → send notification and/or play sound). No need for full home-automation stack initially.

**Deliverables:**

- [ ] Summary and optional response suggestion per event (in PWA and optionally in notification).
- [ ] (Optional) Rule-based automation for play sound / notify.

---

## Stage 8 — Native apps and Apple Watch (later)

**Goal:** Dedicated iPhone/Android apps and an Apple Watch app for quick view and “respond with sound.”

**Outcomes:**

- Native apps can use same backend; better background notifications and Watch integration.
- Watch: show latest event and “Respond with sound” or “Mark as seen.”

**Technical notes:**

- **React Native** (or Flutter) for iOS + Android from one codebase; **Swift/SwiftUI** for Watch if you want best Watch experience. Backend stays the same; apps are new clients.
- Reuse PWA flows (mapping, history, sounds) as reference; native adds push reliability and Watch UI.

**Deliverables:**

- [ ] iOS and Android apps (same backend as PWA).
- [ ] Apple Watch companion: last event + quick respond.

---

## Suggested tech stack (current)

| Layer           | Choice              | Notes                                      |
|----------------|---------------------|--------------------------------------------|
| Camera         | Tapo (RTSP)         | Wired Tapo; RTSP enabled; dedicated user  |
| Detection      | Python + OpenCV     | Pi or server; add small CNN if needed      |
| Backend        | FastAPI (Python)    | Async, good for streams and push          |
| DB             | PostgreSQL          | Events, mappings, subscriptions, sounds   |
| Frontend       | React PWA (Vite)    | Installable, web push, one codebase        |
| Push           | Web Push (VAPID)    | One implementation for iOS + Android       |
| Notifications  | PWA first           | Native apps in Stage 8                     |
| Sound playback | Tapo API or Pi+spkr | Depends on Tapo model; TTS via API or Pi  |
| Later          | TensorFlow/PyTorch  | Cat ID, meow, body; Hugging Face for LLM   |

---

## What we can do next

1. **Lock Stage 1:** Confirm Tapo model(s) and that RTSP works from the Pi (or your dev machine), then implement RTSP → OpenCV → event detection → PostgreSQL.
2. **Repository structure:** Add `docs/` (this plan), `backend/` (FastAPI + detector + DB), `pwa/` (React PWA), and optional `scripts/` for one-off tools.
3. **Database schema:** Draft tables for `events`, `button_mappings`, `push_subscriptions`, `sounds` so we can start coding against them.

If you tell me your Tapo model (e.g. C100, C200) and whether you prefer to run the detector on the Pi or your laptop first, we can break Stage 1 into concrete tasks and start with the first one (e.g. “RTSP connection + save one frame every N seconds” then “motion in regions → events”).
