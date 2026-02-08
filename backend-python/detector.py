"""
Detector stub for backend init. RTSP + motion detection is implemented on a separate feature branch.
Run from backend-python: python -m detector (or from repo root: cd backend-python && python -m detector).
"""
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run_detector() -> None:
    """
    Stub: no RTSP or motion detection yet. Implement on the detector feature branch.
    """
    logger.info("Detector stub: RTSP motion detection not implemented. Use the detector feature branch for Stage 1 detection.")


if __name__ == "__main__":
    run_detector()
