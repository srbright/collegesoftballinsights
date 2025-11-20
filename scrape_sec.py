# scrape_sec.py
import json
import asyncio
from platforms.sidearm import fetch_roster
import aiohttp
import os

INPUT_JSON = "teams_sec.json"  # Your list of SEC teams
OUTPUT_JSON = "outputs/softball_sec.json"

async def scrape_team(session, team):
    print(f"[info] Scraping {team['school']} at {team.get('url')}")
    players = await fetch_roster(session, team.get("url", ""))
    team["players"] = players

    # Add dummy fields if missing
    team.setdefault("roster_year", 2026)
    team.setdefault("three_year_avg", len(players))
    team.setdefault("retention_rate", 0.95)
    team.setdefault("coach", {"name": "N/A", "years": 0})
    team.setdefault("facilities", {"stadium":"N/A","capacity":0,"lights":False,"indoor":False,"turf":"N/A"})

    return team

async def main():
    if not os.path.exists(INPUT_JSON):
        print(f"[error] Input JSON {INPUT_JSON} not found!")
        return

    with open(INPUT_JSON) as f:
        teams = json.load(f)

    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[scrape_team(session, t) for t in teams])

    os.makedirs("outputs", exist_ok=True)
    with open(OUTPUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[info] JSON successfully written to {OUTPUT_JSON}")

if __name__ == "__main__":
    asyncio.run(main())
