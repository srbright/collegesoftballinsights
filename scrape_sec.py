# scrape_sec.py
import asyncio
import aiohttp
import json
import os
from platforms import sidearm

# --- Paths ---
DATA_PATH = os.path.join("data", "teams_sec.json")
OUTPUT_PATH = os.path.join("outputs", "softball_sec.json")

# --- Utility functions ---
def load_teams():
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def save_output(data):
    os.makedirs("outputs", exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[info] Saved output to {OUTPUT_PATH}")

def calculate_retention(team):
    """
    Computes retention / transfer rates over last 3 years
    Placeholder: implement actual roster comparison if storing previous rosters
    """
    roster_history = team.get("roster_history", [])
    if len(roster_history) < 2:
        return {"retention_rate": None, "transfers_in": 0, "transfers_out": 0}
    # naive example: compare roster counts
    prev = roster_history[-2].get("total", 0)
    curr = roster_history[-1].get("total", 0)
    retention_rate = round(curr / prev, 2) if prev else None
    return {"retention_rate": retention_rate, "transfers_in": 0, "transfers_out": 0}

def add_three_year_avg(team):
    rosters = [r.get("total", 0) for r in team.get("roster_history", [])[-3:]]
    if rosters:
        team["three_year_avg"] = round(sum(rosters) / len(rosters), 2)
    else:
        team["three_year_avg"] = None
    return team

# --- Scraper main ---
async def scrape_team(team, session):
    """
    Scrapes one SEC team
    """
    print(f"[info] Scraping {team['school']} ...")
    years_to_try = [2026, 2025, 2024]

    roster = None
    for year in years_to_try:
        team["_requested_year"] = year
        try:
            result = await sidearm.scraper(team, session)
            if result["roster"]:
                roster = result["roster"]
                team["roster_year"] = year
                break
        except Exception as e:
            print(f"[warn] {team['school']} {year} scrape failed: {e}")

    if roster is None:
        print(f"[warn] No roster found for {team['school']}. Using empty roster.")
        roster = []

    # Add roster info
    team["players"] = roster
    team["roster_history"] = [
        {"year": team.get("roster_year", 2026), "total": len(roster)}
    ]

    # Add retention / transfers
    team.update(calculate_retention(team))

    # Add 3-year average
    team = add_three_year_avg(team)

    # Coach placeholder (could scrape later)
    team["coach"] = {"name": team.get("coach_name", "TBD"), "years": team.get("coach_years", 0)}

    # Facilities placeholder (could scrape later)
    team["facilities"] = team.get("facilities", {})

    return team

async def main():
    teams = load_teams()
    results = []

    async with aiohttp.ClientSession() as session:
        tasks = [scrape_team(team, session) for team in teams]
        results = await asyncio.gather(*tasks)

    save_output(results)

if __name__ == "__main__":
    asyncio.run(main())
