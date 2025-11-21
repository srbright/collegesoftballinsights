# scrape_sec.py
import json
import asyncio
import aiohttp
import os
from platforms.sidearm import fetch_roster

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
    "Vanderbilt": (36.1447, -86.8027),
}

def normalize_roster_url(raw: str) -> str:
    """
    Make sure we hit the actual roster page.
    If URL doesn't contain 'roster', append '/roster'.
    """
    if not raw:
        return ""
    url = raw.strip()
    low = url.rstrip("/").lower()
    if "roster" not in low:
        url = url.rstrip("/") + "/roster"
    return url

async def scrape_team(session, team):
    school = team.get("school", "Unknown")
    print(f"[info] Scraping {school}")

    # lat/lng
    if school in LAT_LNG:
        team["latitude"], team["longitude"] = LAT_LNG[school]
    else:
        team["latitude"] = None
        team["longitude"] = None

    # figure out roster URL
    base_url = team.get("softball_url") or team.get("url") or ""
    roster_url = normalize_roster_url(base_url)

    # fetch roster
    players = await fetch_roster(session, roster_url)
    team["players"] = players
    team["rosterSize"] = len(players)

    # quick aggregates
    class_counts = {}
    pos_counts = {}
    for p in players:
        cls = p.get("class", "").strip()
        pos = p.get("pos", "").strip()
        if cls:
            class_counts[cls] = class_counts.get(cls, 0) + 1
        if pos:
            pos_counts[pos] = pos_counts.get(pos, 0) + 1

    team["classCounts"] = class_counts
    team["posCounts"] = pos_counts

    # placeholders for now
    team["coach"] = {"name": "TBD", "years": 0}
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
        results = []
        for t in teams:
            try:
                updated = await scrape_team(session, t)
                results.append(updated)
            except Exception as e:
                print(f"[error] failed scraping {t.get('school')}: {e}")

    with open(OUTPUT_JSON, "w") as f:
        json.dump(results, f, indent=2)

    print(f"[info] Wrote {OUTPUT_JSON} with {len(results)} teams")

if __name__ == "__main__":
    asyncio.run(main())
