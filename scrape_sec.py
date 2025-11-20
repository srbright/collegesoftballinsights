name: Scrape SEC Softball

on:
  schedule:
    - cron: '0 6 * * *'     # runs daily at 6AM UTC
  workflow_dispatch:         # allows manual runs

permissions:
  contents: write            # REQUIRED so the bot can push JSON

jobs:
  scrape:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repo
      uses: actions/checkout@v3
      with:
        persist-credentials: true   # REQUIRED for push to work

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.11

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install aiohttp beautifulsoup4 lxml

    - name: Run scraper
      run: |
        python scrape_sec.py || echo "[ERROR] scrape_sec.py failed!"

    - name: Move JSON if exists
      run: |
        mkdir -p outputs
        if [ -f outputs/softball_sec.json ]; then
          mv outputs/softball_sec.json ./softball_sec.json
          echo "JSON moved to root."
        else
          echo "[WARN] outputs/softball_sec.json not found."
        fi

    - name: Commit and push JSON
      run: |
        git config --global user.name "github-actions[bot]"
        git config --global user.email "github-actions[bot]@users.noreply.github.com"
        git add softball_sec.json || echo "nothing to add"
        git commit -m "Update SEC JSON [skip ci]" || echo "No changes to commit"
        git push || echo "[WARN] Push failed"
