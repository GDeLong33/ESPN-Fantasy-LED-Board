import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TEAM_IDS = {1, 10, 6, 15}

# Get configuration from environment variables
LEAGUE_ID = os.getenv("LEAGUE_ID")
PLATFORM_VERSION = os.getenv("PLATFORM_VERSION")

if not LEAGUE_ID or not PLATFORM_VERSION:
    raise ValueError("LEAGUE_ID and PLATFORM_VERSION environment variables must be set")

url = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2026/segments/0/leagues/{LEAGUE_ID}"
params = {
    "view": ["mMatchup", "mMatchupScore", "mTeam"],
    "scoringPeriodId": 1,
    "platformVersion": PLATFORM_VERSION,
}

response = requests.get(url, params=params)

data = response.json()

if response.status_code == 200:
    print("Request successful!")
if response.status_code == 400:
    print("Error: Bad Request. Please check the URL and parameters.")

teams = data["teams"]
scores = data['schedule']
scoringPeriodId = data['scoringPeriodId']
for team in teams:
    if(team["id"] in TEAM_IDS and scoringPeriodId == 1):
        print(f"ID: {team['id']}")
        print(f"Name: {team['name']}") 
        for score in scores:
            for side in ("home", "away"):
                if side in score and score[side]["teamId"] == team["id"]:
                    print(f"Score: {score[side]['totalPoints']}")
