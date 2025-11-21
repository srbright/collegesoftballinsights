# platforms/sidearm.py
import aiohttp
from bs4 import BeautifulSoup

async def fetch_roster(session, url: str):
    players = []

    if not url:
        print("[error] fetch_roster called with empty URL")
        return players

    print(f"[debug] fetching roster from: {url}")

    try:
        async with session.get(url) as resp:
            if resp.status != 200:
                print(f"[error] HTTP {resp.status} for {url}")
                return players
            html = await resp.text()
    except Exception as e:
        print(f"[error] request failed at {url}: {e}")
        return players

    soup = BeautifulSoup(html, "lxml")

    # --- SEC Modern Sidearm Layout ---
    cards = soup.select(".sidearm-roster-player-card")
    if cards:
        for c in cards:
            name  = (c.select_one(".sidearm-roster-player-card-name") or "").get_text(strip=True)
            pos   = (c.select_one(".sidearm-roster-player-card-position") or "").get_text(strip=True)
            year  = (c.select_one(".sidearm-roster-player-card-academic-year") or "").get_text(strip=True)
            num   = (c.select_one(".sidearm-roster-player-card-jersey-number") or "").get_text(strip=True)

            if name:
                players.append({
                    "name": name,
                    "pos": pos,
                    "class": year,
                    "number": num
                })

        print(f"[debug] parsed {len(players)} SEC card players")
        return players

    print(f"[warn] no recognizable roster layout at {url}")
    return players
