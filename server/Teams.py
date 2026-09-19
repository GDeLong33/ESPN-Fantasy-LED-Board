import os
from datetime import date

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables
LEAGUE_ID = os.getenv("LEAGUE_ID")
PLATFORM_VERSION = os.getenv("PLATFORM_VERSION")
SEASON = os.getenv("SEASON", str(date.today().year))
TEAM_IDS = [int(t) for t in os.getenv("TEAM_IDS", "1,10,6,15").split(",")]

# Optional: only needed if ESPN ever stops serving the league without auth
SWID = os.getenv("SWID")
ESPN_S2 = os.getenv("ESPN_S2")

if not LEAGUE_ID or not PLATFORM_VERSION:
    raise ValueError("LEAGUE_ID and PLATFORM_VERSION environment variables must be set")

URL = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{SEASON}/segments/0/leagues/{LEAGUE_ID}"
PARAMS = {
    "view": ["mMatchup", "mMatchupScore", "mTeam"],
    "platformVersion": PLATFORM_VERSION,
}
COOKIES = {"SWID": SWID, "espn_s2": ESPN_S2} if SWID and ESPN_S2 else None


def fetch_scores():
    """Fetch the current week's live score for each team in TEAM_IDS.

    Returns {"week": int, "teams": [{"id", "name", "score"}, ...]}.
    A team with no matchup this week (bye) gets a score of None.
    Raises requests.RequestException / KeyError if ESPN fails or changes shape.
    """
    response = requests.get(URL, params=PARAMS, cookies=COOKIES, timeout=10)
    response.raise_for_status()
    data = response.json()

    week = data["scoringPeriodId"]  # current week, as reported by ESPN

    # schedule contains the whole season, so keep only the current week's matchups
    current_matchups = [m for m in data["schedule"] if m["matchupPeriodId"] == week]

    # totalPoints stays 0 until the week is final; totalPointsLive updates during games
    live_scores = {}
    for matchup in current_matchups:
        for side in ("home", "away"):
            if side in matchup:
                live_scores[matchup[side]["teamId"]] = matchup[side]["totalPointsLive"]

    names = {team["id"]: team["name"] for team in data["teams"]}

    return {
        "week": week,
        "teams": [
            {"id": team_id, "name": names.get(team_id, f"Team {team_id}"), "score": live_scores.get(team_id)}
            for team_id in TEAM_IDS
        ],
    }


if __name__ == "__main__":
    result = fetch_scores()
    print(f"Week {result['week']}")
    for team in result["teams"]:
        print(f"ID: {team['id']}")
        print(f"Name: {team['name']}")
        print(f"Score: {team['score']}")
