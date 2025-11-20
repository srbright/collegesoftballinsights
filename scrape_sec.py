# scrape_sec.py
import json
import asyncio
import aiohttp
import os
from platforms.sidearm import fetch_roster

INPUT_JSON = "teams_sec.json"
OUTPUT_JSON = "outputs/softball_sec.json"

async def scrape_team(session, team: dict) -> dict:
    url = team["softball_url"]  # IMPORTANT: use softball_url from teams_sec.json
    print(f"[info] Scraping {team['school']} at {url}")

    players = await fetch_roster(session, url)
    print(f"[info] {team['school']}: scraped {len(players)} players")

    team["players"] = players

    # Simple placeholders for now
    team["roster_year"] = 2026
    team["three_year_avg"] = len(players)
    team["retention_rate"] = 1.0 if players else 0.0
    team["coach"] = {"name": "TBD", "years": 0}
    team["facilities"] = {
        "stadium": "TBD",
        "capacity": 0,
        "lights": False,
        "indoor": False,
        "turf": "Unknown"
    }

    return team

async def main():
    if not os.path.exists(INPUT_JSON):
        print(f"[error] {INPUT_JSON} not found!")
        return

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        teams = json.load(f)

    os.makedirs("outputs", exist_ok=True)

    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(
            *[scrape_team(session, t) for t in teams]
        )

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"[info] JSON successfully written to {OUTPUT_JSON}")

if __name__ == "__main__":
    asyncio.run(main())
