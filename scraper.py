import requests
from bs4 import BeautifulSoup
import json
from time import sleep
import random

# Sample URLs — replace with your full 1,600 list
teams = [
  {'name': 'Oklahoma Sooners', 'url': 'https://soonersports.com/sports/softball/roster'},
  {'name': 'Texas Longhorns', 'url': 'https://texassports.com/sports/softball/roster'},
  # ... add all from step 1 (use a CSV reader for large lists)
]

user_agents = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
  'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1'
]

def scrape_team(url, team_name):
  headers = {'User-Agent': random.choice(user_agents)}
  try:
    res = requests.get(url, headers=headers, timeout=10)
    res.raise_for_status()
  except Exception as e:
    print(f"Error scraping {team_name}: {e}")
    return {"name": team_name, "players": [], "error": str(e)}

  soup = BeautifulSoup(res.text, 'html.parser')
  players = []
  for row in soup.find_all('tr', class_='sidearm-roster-player'):
    name = row.find('td', class_='sidearm-roster-player-name').text.strip() if row.find('td', class_='sidearm-roster-player-name') else ''
    pos = row.find('td', class_='sidearm-roster-player-position').text.strip() if row.find('td', class_='sidearm-roster-player-position') else ''
    cl = row.find('td', class_='sidearm-roster-player-class').text.strip() if row.find('td', class_='sidearm-roster-player-class') else ''
    if name:
      players.append({'name': name, 'pos': pos, 'class': cl})
  sleep(random.uniform(2, 5))  # Anti-block delay

  # Aggregates
  total = len(players)
  freshmen = sum(1 for p in players if 'Fr' in p['class'])
  transfers = sum(1 for p in players if 'Tr' in p['class'] or 'Gr' in p['class'])  # Rough estimate
  newcomers = freshmen + transfers
  net = total - 25  # Assume average prior size; customize
  return {"name": team_name, "total_players": total, "newcomers": newcomers, "net": net, "players": players}

# Batch scrape to scale
batch_size = 50  # Run 50/day to avoid blocks
data = []
for i in range(0, len(teams), batch_size):
  batch = teams[i:i+batch_size]
  batch_data = [scrape_team(t['url'], t['name']) for t in batch]
  data.extend(batch_data)
  print(f"Batch {i//batch_size + 1} complete — sleeping 1 min")
  sleep(60)  # Batch delay

# Save as one JSON or split
with open('all_teams.json', 'w') as f:
  json.dump(data, f, indent=2)
print("Full scrape complete — all_teams.json updated!")
