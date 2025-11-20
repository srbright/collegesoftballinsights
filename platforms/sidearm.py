# sidearm.py
import aiohttp
from bs4 import BeautifulSoup

async def fetch_roster(session, url):
    """
    Fetches a roster page and returns structured player data.
    """
    try:
        async with session.get(url) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, "lxml")
            players = []

            # Example parsing logic (adjust to actual Sidearm structure)
            table = soup.find("table")
            if not table:
                print(f"[warn] No table found at {url}")
                return players

            for row in table.find_all("tr")[1:]:
                cols = row.find_all("td")
                if len(cols) < 4:
                    continue
                player = {
                    "number": cols[0].get_text(strip=True),
                    "name": cols[1].get_text(strip=True),
                    "pos": cols[2].get_text(strip=True),
                    "class": cols[3].get_text(strip=True),
                }
                players.append(player)
            return players
    except Exception as e:
        import traceback
        print(f"[error] Failed to fetch {url}:\n{traceback.format_exc()}")
        return []
