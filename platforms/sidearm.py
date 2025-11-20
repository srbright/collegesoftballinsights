import aiohttp
from bs4 import BeautifulSoup

async def fetch_roster(session, url):
    players = []

    try:
        async with session.get(url) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, "lxml")

            roster_blocks = soup.select(".sidearm-roster-player")

            if not roster_blocks:
                print(f"[WARN] No roster blocks found at {url}")
                return players

            for block in roster_blocks:
                name_tag = block.select_one(".sidearm-roster-player-name h3")
                pos_tag = block.select_one(".sidearm-roster-player-position")
                class_tag = block.select_one(".sidearm-roster-player-academic-year")
                number_tag = block.select_one(".sidearm-roster-player-jersey-number")

                player = {
                    "name": name_tag.get_text(strip=True) if name_tag else "",
                    "pos": pos_tag.get_text(strip=True) if pos_tag else "",
                    "class": class_tag.get_text(strip=True) if class_tag else "",
                    "number": number_tag.get_text(strip=True) if number_tag else ""
                }

                players.append(player)

    except Exception as e:
        print(f"[ERROR] Failed roster scrape for {url}: {e}")

    return players
