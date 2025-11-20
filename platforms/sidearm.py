# platforms/sidearm.py
import aiohttp
from bs4 import BeautifulSoup

async def fetch_roster(session, url: str):
    players = []

    if not url:
        print("[error] fetch_roster called with empty URL")
        return players

    print(f"[debug] fetch_roster url={url}")

    try:
        async with session.get(url) as resp:
            if resp.status != 200:
                print(f"[error] HTTP {resp.status} for {url}")
                return players
            html = await resp.text()
    except Exception as e:
        print(f"[error] request failed for {url}: {e}")
        return players

    soup = BeautifulSoup(html, "lxml")

    # ---------- SEC Sidearm Modern Layout ----------
    cards = soup.select(".sidearm-roster-player-card")
    if cards:
        for c in cards:
            name_tag  = c.select_one(".sidearm-roster-player-card-name")
            pos_tag   = c.select_one(".sidearm-roster-player-card-position")
            year_tag  = c.select_one(".sidearm-roster-player-card-academic-year")
            num_tag   = c.select_one(".sidearm-roster-player-card-jersey-number")

            name  = name_tag.get_text(strip=True) if name_tag else ""
            pos   = pos_tag.get_text(strip=True) if pos_tag else ""
            year  = year_tag.get_text(strip=True) if year_tag else ""
            number = num_tag.get_text(strip=True) if num_tag else ""

            if name:
                players.append({
                    "name": name,
                    "pos": pos,
                    "class": year,
                    "number": number
                })

        print(f"[debug] Parsed {len(players)} SEC card players at {url}")
        return players

    # ---------- Old Sidearm fallback ----------
    blocks = soup.select(".sidearm-roster-player")
    if blocks:
        for b in blocks:
            name_tag = b.select_one(".sidearm-roster-player-name h3, .sidearm-roster-player-name a")
            pos_tag = b.select_one(".sidearm-roster-player-position")
            year_tag = b.select_one(".sidearm-roster-player-academic-year")
            num_tag = b.select_one(".sidearm-roster-player-jersey-number")

            name = name_tag.get_text(strip=True) if name_tag else ""
            pos = pos_tag.get_text(strip=True) if pos_tag else ""
            year = year_tag.get_text(strip=True) if year_tag else ""
            number = num_tag.get_text(strip=True) if num_tag else ""

            if name:
                players.append({
                    "name": name,
                    "pos": pos,
                    "class": year,
                    "number": number
                })

        print(f"[debug] Parsed {len(players)} old layout players at {url}")
        return players

    print(f"[warn] No recognizable roster layout at {url}")
    return players
