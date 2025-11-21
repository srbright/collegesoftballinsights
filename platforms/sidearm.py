# platforms/sidearm.py
import aiohttp
from bs4 import BeautifulSoup

async def fetch_roster(session, url: str):
    """
    Fetches a softball roster from a Sidearm-style athletics page.
    Returns a list of players: [{name, pos, class, number}, ...]
    Supports:
      - New Sidearm layout (.s-person-card, used by Alabama, etc.)
      - Legacy Sidearm card layout (.sidearm-roster-player)
      - Simple table fallback
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

    # ------------------------------------------------------------------
    # 1) NEW SIDEARM LAYOUT (.s-person-card)
    #    Example text inside each card:
    #    "Jersey Number 00 Vic Moten Position RHP Academic Year Fr. ..."
    # ------------------------------------------------------------------
    def parse_new_sidearm_layout():
        found = []
        cards = soup.select(".s-person-card")

        for card in cards:
            texts = list(card.stripped_strings)
            # Players have "Academic Year"; staff typically does not
            if "Academic Year" not in texts:
                continue

            def get_after(label: str):
                try:
                    i = texts.index(label)
                except ValueError:
                    return ""
                return texts[i + 1] if i + 1 < len(texts) else ""

            # Name is usually right before "Position"
            name = ""
            try:
                pos_label_idx = texts.index("Position")
                if pos_label_idx > 0:
                    name = texts[pos_label_idx - 1]
            except ValueError:
                # No "Position" label → not a player
                continue

            number = get_after("Jersey Number")
            pos = get_after("Position")
            year = get_after("Academic Year")

            if name:
                found.append({
                    "name": name,
                    "pos": pos,
                    "class": year,
                    "number": number,
                })

        if found:
            print(f"[debug] parsed {len(found)} players using .s-person-card at {url}")
        return found

    players = parse_new_sidearm_layout()
    if players:
        return players

    # ------------------------------------------------------------------
    # 2) LEGACY SIDEARM CARD LAYOUT (.sidearm-roster-player)
    # ------------------------------------------------------------------
    blocks = soup.select(".sidearm-roster-player")
    if blocks:
        for block in blocks:
            name_tag = block.select_one(
                ".sidearm-roster-player-name h3, .sidearm-roster-player-name a"
            )
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
                    "number": number,
                })

        print(f"[debug] parsed {len(players)} players using legacy layout at {url}")
        return players

    # ------------------------------------------------------------------
    # 3) Fallback: simple <table> layout
    # ------------------------------------------------------------------
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
                    "number": number,
                })

        print(f"[debug] parsed {len(players)} players using table layout at {url}")
        return players

    print(f"[warn] no roster layout recognized at {url}")
    return players
