# scrape_sec.py
import json
import asyncio
from platforms.sidearm import fetch_roster
import aiohttp
import os

INPUT_JSON = "teams_sec.json"
OUTPUT_JSON = "softball_sec.json"

# Static geo lookup for SEC campuses
LAT_LNG = {
    "Alabama": (33.2098, -87.5692),
    "Arkansas": (36.0687, -94.1740),
    "Auburn": (32.5900, -85.5000),
    "Florida": (29.6516, -82.3248),
    "Georgia": (33.9480, -83.3773),
    "Kentucky": (38.0300, -84.5037),
    "LSU": (30.4133, -91.1800),
    "Mississippi State": (33.4504, -88.8184),
    "Missouri": (38.9453, -92.3289),
    "Ole Miss": (34.3659, -89.5380),
    "South Carolina": (33.9950, -81.0270),
    "Tennessee": (35.9545, -83.9295),
    "Texas A&M": (30.6150, -96.3400),
    "Vanderbilt": (36.1447, -86.8027)
}


async def scrape_team(session, team):
    school = team["school"]

    print(f"[info] Scraping {school}")

    # 1) Add lat/lng
    if school in LAT_LNG:
        team["latitude"], team["longitude"] = LAT_LNG[school]
    else:
        team["latitude"] = None
        team["longitude"] = None

    # 2) Fetch roster
    roster_url = team.get("softball_url") or team.get("url")
    players = await fetch_roster(session, roster_url)
    team["players"] = players
    team["rosterSize"] = len(players)

    # 3) Derive quick stats
    class_counts = {}
    pos_counts = {}

    for p in players:
        class_counts[p.get("class", "")] = class_counts.get(p.get("class", ""), 0) + 1
        pos_counts[p.get("pos", "")] = pos_counts.get(p.get("pos", ""), 0) + 1

    team["classCounts"] = class_counts
    team["posCounts"] = pos_counts

    # 4) Placeholder advanced recruiting data
    team["coach"] = {
        "name": "TBD",
        "years": 0
    }

    team["retentionRate"] = 1.0
    team["transfersIn"] = 0
    team["transfersOut"] = 0
    team["rosterYear"] = 2025

    return team


async def main():
    if not os.path.exists(INPUT_JSON):
        print(f"[error] Missing {INPUT_JSON}")
        return

    with open(INPUT_JSON) as f:
        teams = json.load(f)

    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[
            scrape_team(session, t)
            for t in teams
        ])

    with open(OUTPUT_JSON, "w") as f:
        json.dump(results, f, indent=2)

    print(f"[info] Wrote {OUTPUT_JSON}")


if __name__ == "__main__":
    asyncio.run(main())
