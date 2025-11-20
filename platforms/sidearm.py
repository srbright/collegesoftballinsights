# platforms/sidearm.py
import aiohttp
from bs4 import BeautifulSoup

async def fetch_roster(session, url: str):
    """
    Fetches a softball roster from a Sidearm-style athletics page.
    Returns a list of players: [{name, pos, class, number}, ...]
    """
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

    # 1) Try Sidearm card layout first (most SEC schools use this)
    blocks = soup.select(".sidearm-roster-player")
    if blocks:
        for block in blocks:
            name_tag = block.select_one(".sidearm-roster-player-name h3, .sidearm-roster-player-name a")
            pos_tag = block.select_one(".sidearm-roster-player-position")
            class_tag = block.select_one(".sidearm-roster-player-academic-year")
            num_tag = block.select_one(".sidearm-roster-player-jersey-number")

            name = name_tag.get_text(strip=True) if name_tag else ""
            pos = pos_tag.get_text(strip=True) if pos_tag else ""
            year = class_tag.get_text(strip=True) if class_tag else ""
            number = num_tag.get_text(strip=True) if num_tag else ""

            if name:
                players.append({
                    "name": name,
                    "pos": pos,
                    "class": year,
                    "number": number
                })

        print(f"[debug] parsed {len(players)} players using card layout at {url}")
        return players

    # 2) Fallback: simple table (for any non-Sidearm pages)
    table = soup.find("table")
    if table:
        rows = table.find_all("tr")
        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) < 4:
                continue
            number = cols[0].get_text(strip=True)
            name = cols[1].get_text(strip=True)
            pos = cols[2].get_text(strip=True)
            year = cols[3].get_text(strip=True)
            if name:
                players.append({
                    "name": name,
                    "pos": pos,
                    "class": year,
                    "number": number
                })

        print(f"[debug] parsed {len(players)} players using table layout at {url}")
        return players

    print(f"[warn] no roster layout recognized at {url}")
    return players
