# platforms/sidearm.py
import aiohttp
from bs4 import BeautifulSoup
import re

async def scrape_coaches(team, session):
    """
    Scrapes Sidearm Coaches tab for head coach info.
    Returns: {"head_coach": {"name": str, "years": int}, "all_coaches": [...]}
    """
    base_url = team.get("softball_url")
    # Often coaches are at /staff
    staff_url = base_url.rstrip("/") + "/staff/"

    try:
        async with session.get(staff_url) as resp:
            if resp.status != 200:
                return {"head_coach": {"name": "TBD", "years": 0}, "all_coaches": []}
            html = await resp.text()
    except Exception:
        return {"head_coach": {"name": "TBD", "years": 0}, "all_coaches": []}

    soup = BeautifulSoup(html, "lxml")
    coaches = []

    # heuristic: div with class 'sidearm-roster-player' or 'staff-card'
    staff_cards = soup.find_all("div", class_=re.compile(r"staff-card|sidearm-roster-player"))
    for card in staff_cards:
        try:
            name_tag = card.find("h3") or card.find("a")
            name = name_tag.get_text(strip=True) if name_tag else "Unknown"

            title_tag = card.find("p", class_=re.compile(r"title"))
            title = title_tag.get_text(strip=True) if title_tag else ""

            # Try to extract years from text like "Head Coach (5th season)"
            years_match = re.search(r"(\d+)(?:th|rd|st|nd)\s*season", title, re.I)
            years = int(years_match.group(1)) if years_match else 0

            coaches.append({"name": name, "title": title, "years": years})
        except:
            continue

    # Pick head coach heuristically
    head = next((c for c in coaches if "head coach" in c.get("title", "").lower()), None)
    if not head and coaches:
        head = coaches[0]

    return {"head_coach": head or {"name": "TBD", "years": 0}, "all_coaches": coaches}


async def scrape_facilities(team, session):
    """
    Scrapes facilities info for the team. Returns dict:
    {"stadium": str, "capacity": int, "lights": bool, "indoor": bool, "turf": str}
    """
    base_url = team.get("softball_url")
    # Many Sidearm sites have /facilities page
    fac_url = base_url.rstrip("/") + "/facilities/"

    try:
        async with session.get(fac_url) as resp:
            if resp.status != 200:
                return {}
            html = await resp.text()
    except Exception:
        return {}

    soup = BeautifulSoup(html, "lxml")
    facilities = {}

    # Heuristic: look for stadium name
    name_tag = soup.find(["h1", "h2", "h3"], string=re.compile(r"stadium|field", re.I))
    facilities["stadium"] = name_tag.get_text(strip=True) if name_tag else "Unknown"

    # Capacity
    cap_tag = soup.find(string=re.compile(r"Capacity", re.I))
    if cap_tag:
        match = re.search(r"(\d[\d,]*)", cap_tag)
        if match:
            facilities["capacity"] = int(match.group(1).replace(",", ""))
        else:
            facilities["capacity"] = 0

    # Lights (simple keyword search)
    facilities["lights"] = bool(re.search(r"lights", html, re.I))
    # Indoor (simple keyword search)
    facilities["indoor"] = bool(re.search(r"indoor", html, re.I))
    # Turf type
    turf_match = re.search(r"(grass|turf|artificial)", html, re.I)
    facilities["turf"] = turf_match.group(1).capitalize() if turf_match else "Unknown"

    return facilities
