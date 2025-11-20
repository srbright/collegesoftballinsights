# platforms/sidearm.py
import aiohttp
from bs4 import BeautifulSoup
import asyncio
import re

async def scrape_sidearm_roster(team, session):
    """
    Scrapes Sidearm-hosted roster pages for NCAA softball.
    team: dict with 'softball_url' and optional '_requested_year' (2026, 2025, etc.)
    session: aiohttp.ClientSession
    Returns:
        {
            "roster": [
                {"name": str, "pos": str, "class": str, "number": str, "hometown": str, "highschool": str, ...}
            ],
            "scraped_url": final_url
        }
    """
    base_url = team.get("softball_url")
    year = team.get("_requested_year", None)
    final_url = base_url

    # Try to append season query if year is provided
    if year:
        # Sidearm often uses /season/YYYY
        if base_url.endswith("/"):
            final_url = f"{base_url}{year}/"
        else:
            final_url = f"{base_url}/{year}/"

    async with session.get(final_url) as resp:
        if resp.status != 200:
            # fallback: try base URL without year
            final_url = base_url
            async with session.get(final_url) as resp2:
                if resp2.status != 200:
                    raise Exception(f"Sidearm scrape failed for {team.get('school')} ({final_url})")
                html = await resp2.text()
        else:
            html = await resp.text()

    soup = BeautifulSoup(html, "lxml")

    roster_list = []

    # Sidearm roster table is usually in a div with class 'sidearm-roster-player' or table row 'tr'
    players = soup.find_all("tr")
    if not players:
        # fallback: look for 'div' cards
        players = soup.find_all("div", class_=re.compile(r"sidearm-roster-player"))

    for p in players:
        try:
            name = None
            pos = None
            class_year = None
            number = None
            hometown = None
            highschool = None

            # Extract text fields heuristically
            # common Sidearm structure: <td class="sidearm-roster-player-name"><a>Player Name</a></td>
            td_name = p.find("td", class_=re.compile(r"name"))
            if td_name:
                name = td_name.get_text(strip=True)

            td_pos = p.find("td", class_=re.compile(r"position"))
            if td_pos:
                pos = td_pos.get_text(strip=True)

            td_class = p.find("td", class_=re.compile(r"class"))
            if td_class:
                class_year = td_class.get_text(strip=True)

            td_number = p.find("td", class_=re.compile(r"number"))
            if td_number:
                number = td_number.get_text(strip=True)

            td_hometown = p.find("td", class_=re.compile(r"hometown"))
            if td_hometown:
                hometown = td_hometown.get_text(strip=True)

            td_highschool = p.find("td", class_=re.compile(r"highschool|school"))
            if td_highschool:
                highschool = td_highschool.get_text(strip=True)

            if name:  # only include valid entries
                roster_list.append({
                    "name": name,
                    "pos": pos or "Unknown",
                    "class": class_year or "Unknown",
                    "number": number or None,
                    "hometown": hometown or None,
                    "highschool": highschool or None
                })
        except Exception as e:
            print(f"[warn] parsing player: {e}")

    return {"roster": roster_list, "scraped_url": final_url}


# async wrapper to integrate with scrape_sec.py
async def scraper(team, session):
    return await scrape_sidearm_roster(team, session)
