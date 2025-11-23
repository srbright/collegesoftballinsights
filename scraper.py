import json
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import random
from time import sleep

# Your team list (expand as needed)
teams = [
  {'name': 'Oklahoma Sooners', 'url': 'https://soonersports.com/sports/softball/roster'},
  {'name': 'Texas Longhorns', 'url': 'https://texassports.com/sports/softball/roster'},
  # Add more teams...
]

def scrape_team(url, team_name):
  print(f"Scraping {team_name}...")
  players = []

  with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until='domcontentloaded')
    page.wait_for_timeout(random.randint(3000, 6000))  # Wait for JS
    html = page.content()
    browser.close()

  soup = BeautifulSoup(html, 'html.parser')
  rows = soup.find_all('tr', class_='sidearm-roster-player')
  for row in rows:
    name = row.find('td', class_='sidearm-roster-player-name').text.strip() if row.find('td', class_='sidearm-roster-player-name') else ''
    pos = row.find('td', class_='sidearm-roster-player-position').text.strip() if row.find('td', class_='sidearm-roster-player-position') else ''
    cl = row.find('td', class_='sidearm-roster-player-class').text.strip() if row.find('td', class_='sidearm-roster-player-class') else ''
    if name:
      players.append({'name': name, 'pos': pos, 'class': cl})

  sleep(random.uniform(2, 5))  # Delay for politeness

  # Aggregates
  total = len(players)
  freshmen = sum(1 for p in players if 'Fr' in p['class'])
  transfers = sum(1 for p in players if 'Tr' in p['class'] or 'Gr' in p['class'])
  newcomers = freshmen + transfers
  net = total - 25  # Example prior size

  return {"name": team_name, "total_players": total, "newcomers": newcomers, "net": net, "players": players}

# Run and save
data = []
for t in teams:
  result = scrape_team(t['url'], t['name'])
  data.append(result)
  print(f"{t['name']}: {len(result['players'])} players scraped")

with open('all_teams.json', 'w') as f:
  json.dump(data, f, indent=2)
print("Saved to all_teams.json!")
