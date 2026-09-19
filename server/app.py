import logging
import os
import threading
import time
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:  # Python 3.8
    from backports.zoneinfo import ZoneInfo

from dotenv import load_dotenv
from flask import Flask, jsonify

from Teams import fetch_scores

load_dotenv()

PORT = int(os.getenv("PORT", "8080"))
GAME_POLL_SECONDS = int(os.getenv("GAME_POLL_SECONDS", "30"))   # during NFL game windows
IDLE_POLL_SECONDS = int(os.getenv("IDLE_POLL_SECONDS", "900"))  # the rest of the week
RETRY_SECONDS = int(os.getenv("RETRY_SECONDS", "60"))           # after a failed fetch

ET = ZoneInfo("America/New_York")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("espn-led")

app = Flask(__name__)

# Latest payload, replaced wholesale by the poller and read by the request handler
state = {"ok": False, "error": "no data yet", "week": None, "teams": [], "updated_at": None}


def in_game_window(now=None):
    """True during the usual NFL windows: Thu night, Sun, Mon night (Eastern time).

    The window runs into the early hours of the next day so late games are covered.
    """
    now = now or datetime.now(ET)
    day, hour = now.weekday(), now.hour  # Monday = 0
    if day == 3 and hour >= 19:  # Thu night
        return True
    if day == 4 and hour < 2:    # Thu night games running past midnight
        return True
    if day == 6 and hour >= 12:  # Sun
        return True
    if day == 0 and (hour < 2 or hour >= 19):  # Sun night spillover, Mon night
        return True
    if day == 1 and hour < 2:    # Mon night spillover
        return True
    return False


def poll_forever():
    while True:
        try:
            result = fetch_scores()
            state.update(ok=True, error=None, updated_at=int(time.time()), **result)
            delay = GAME_POLL_SECONDS if in_game_window() else IDLE_POLL_SECONDS
        except Exception as e:
            # Keep serving the last good scores; just flag that they may be stale
            log.error("ESPN fetch failed: %s", e)
            state.update(ok=False, error=str(e))
            delay = RETRY_SECONDS
        time.sleep(delay)


@app.get("/scores")
def scores():
    return jsonify(state)


@app.get("/health")
def health():
    return jsonify(ok=state["ok"], updated_at=state["updated_at"]), (200 if state["ok"] else 503)


if __name__ == "__main__":
    from waitress import serve

    threading.Thread(target=poll_forever, daemon=True).start()
    log.info("Serving on port %s", PORT)
    serve(app, host="0.0.0.0", port=PORT)
