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

    # Scrape coach info
    coach_data = await sidearm.scrape_coaches(team, session)
    team["coach"] = coach_data.get("head_coach", {"name": "TBD", "years": 0})
    team["coaches_all"] = coach_data.get("all_coaches", [])

    # Scrape facilities
    team["facilities"] = await sidearm.scrape_facilities(team, session)

    return team
