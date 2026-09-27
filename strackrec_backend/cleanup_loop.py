import logging
import os
import re
import signal
import threading
import time
from pathlib import Path

logger = logging.getLogger(__name__)
GENERATED_MBTILES_PATTERN = re.compile(r".+-[0-9a-f]{8}\.mbtiles$")
stop_event = threading.Event()


def cleanup_expired_mbtiles(now: float | None = None) -> int:
    directory = Path(os.environ.get("MBTILES_DIR", "/app/mbtiles"))
    ttl_seconds = int(os.environ.get("MBTILES_TTL_SECONDS", "86400"))
    cutoff = (time.time() if now is None else now) - ttl_seconds
    if not directory.is_dir():
        return 0

    removed = 0
    for path in directory.iterdir():
        if not path.is_file() or not GENERATED_MBTILES_PATTERN.fullmatch(path.name):
            continue
        try:
            if path.stat().st_mtime <= cutoff:
                path.unlink()
                removed += 1
                logger.info("S'ha eliminat el MBTiles caducat %s", path.name)
        except OSError:
            logger.exception("No s'ha pogut eliminar el MBTiles caducat %s", path.name)
    return removed


def _request_stop(signum, frame):
    stop_event.set()


def main() -> None:
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
    signal.signal(signal.SIGTERM, _request_stop)
    signal.signal(signal.SIGINT, _request_stop)
    interval_seconds = int(os.environ.get("MBTILES_CLEANUP_INTERVAL_SECONDS", "3600"))

    while not stop_event.is_set():
        cleanup_expired_mbtiles()
        stop_event.wait(interval_seconds)


if __name__ == "__main__":
    main()
