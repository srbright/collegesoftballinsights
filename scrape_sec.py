# scrape_sec.py
import json
import asyncio
import aiohttp
import os
from platforms.sidearm import fetch_roster

INPUT_JSON = "data/teams_sec.json"
OUTPUT_JSON = "outputs/softball_sec.json"

async def scrape_team(session, team):
    url = team["softball_url"]
    print(f"[info] Scraping {team['school']} → {url}")

    players = await fetch_roster(session, url)
    print(f"[info] {team['school']} players scraped: {len(players)}")

    team["players"] = players
    team["roster_year"] = 2026
    team["three_year_avg"] = len(players)
    team["retention_rate"] = 1.0 if players else 0.0
    team["coach"] = {"name": "TBD", "years": 0}
    team["facilities"] = {"stadium":"TBD"}

    return team

async def main():
    os.makedirs("outputs", exist_ok=True)

    with open(INPUT_JSON, "r") as f:
        teams = json.load(f)

    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[
            scrape_team(session, t) for t in teams
        ])

    with open(OUTPUT_JSON, "w") as f:
        json.dump(results, f, indent=2)

    print("[DONE] SEC JSON written to", OUTPUT_JSON)

if __name__ == "__main__":
    asyncio.run(main())
