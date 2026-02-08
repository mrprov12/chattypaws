"""
Stage 1: Button-press detection from the Tapo C120 RTSP stream.
Reads frames, detects motion in configured regions, writes events to the DB.
Run from backend-python: python -m detector (or from repo root: cd backend-python && python -m detector).
When the camera isn't available yet, the script will retry connecting until it succeeds.
"""
import logging
import time
from pathlib import Path

import cv2
import numpy as np

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

from config import get_settings, get_regions
import db

# How long (seconds) to wait before counting another press in the same region (avoids double-counting).
COOLDOWN_SEC = 2.0
# Motion threshold: mean absolute diff in region above this => "press".
MOTION_THRESHOLD = 25.0
# How often we try to open the stream when it's not available yet.
RETRY_SEC = 10.0


def open_stream(rtsp_url: str):
    """
    Open the RTSP stream with OpenCV. Returns a cv2.VideoCapture or None if it failed.
    """
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        return None
    return cap


def extract_region(frame: np.ndarray, region: dict) -> np.ndarray:
    """Return the grayscale crop for one region (x, y, w, h)."""
    x, y = int(region["x"]), int(region["y"])
    w, h = int(region["w"]), int(region["h"])
    # Clamp to frame bounds.
    h_frame, w_frame = frame.shape[:2]
    x2 = min(x + w, w_frame)
    y2 = min(y + h, h_frame)
    crop = frame[y:y2, x:x2]
    if crop.size == 0:
        return np.array([])
    if len(crop.shape) == 3:
        crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    return crop


def motion_in_region(prev: np.ndarray, curr: np.ndarray, threshold: float = MOTION_THRESHOLD) -> bool:
    """
    True if the mean absolute difference between prev and curr is above threshold.
    Both should be grayscale regions of the same shape.
    """
    if prev.size == 0 or curr.size == 0 or prev.shape != curr.shape:
        return False
    diff = cv2.absdiff(prev, curr)
    return float(np.mean(diff)) > threshold


def run_detector() -> None:
    """
    Main loop: connect to RTSP, read frames, detect motion in regions, insert events.
    If the stream isn't available, retry every RETRY_SEC until it is.
    """
    settings = get_settings()
    regions = get_regions()
    camera_id = settings.camera_id

    # If no regions file, we use one "full frame" region so we can still detect any motion.
    if not regions:
        logger.info("No button_regions.json: using full-frame motion (region_id will be null)")

    last_event_time: dict[str, float] = {}  # region_id -> time of last event

    while True:
        cap = open_stream(settings.rtsp_url)
        if cap is None:
            logger.warning("Could not open RTSP stream (camera off or wrong URL?). Retrying in %s s ...", RETRY_SEC)
            time.sleep(RETRY_SEC)
            continue

        logger.info("Stream opened. Detecting motion (regions=%s). Press Ctrl+C to stop.", len(regions) or "full frame")
        prev_gray: np.ndarray | None = None
        # Use full frame for motion when no regions, else we'll compare per region.
        frame_skip = 2  # Check every Nth frame to reduce CPU
        frame_count = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret or frame is None:
                    logger.warning("Lost frame or stream ended. Reconnecting ...")
                    break

                frame_count += 1
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame

                if prev_gray is None:
                    prev_gray = gray
                    continue

                if frame_count % frame_skip != 0:
                    prev_gray = gray
                    continue

                now = time.time()

                if not regions:
                    # Single full-frame region.
                    if motion_in_region(prev_gray, gray):
                        if now - last_event_time.get("", 0) >= COOLDOWN_SEC:
                            db.insert_event(camera_id, region_id=None, confidence=None)
                            last_event_time[""] = now
                            logger.info("Event (full frame)")
                else:
                    for region in regions:
                        rid = region.get("id", "?")
                        prev_roi = extract_region(prev_gray, region)
                        curr_roi = extract_region(gray, region)
                        if motion_in_region(prev_roi, curr_roi):
                            if now - last_event_time.get(rid, 0) >= COOLDOWN_SEC:
                                db.insert_event(camera_id, region_id=rid, confidence=None)
                                last_event_time[rid] = now
                                logger.info("Event region_id=%s", rid)

                prev_gray = gray

        except KeyboardInterrupt:
            logger.info("Stopped by user")
            break
        finally:
            cap.release()


if __name__ == "__main__":
    run_detector()
