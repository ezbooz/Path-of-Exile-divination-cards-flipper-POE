import json
from urllib.request import Request, urlopen
from datetime import datetime, timezone


def get_current_leagues():
    url = "https://api.pathofexile.com/leagues?type=main"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
    req = Request(url, headers=headers)

    with urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))

    current_time = datetime.now(timezone.utc)
    active_leagues = []

    for league in data:
        end_at = league.get('endAt')
        if end_at is not None:
            end_date = datetime.fromisoformat(end_at.replace('Z', '+00:00'))
            if end_date < current_time:
                continue

        name = league.get('name', '').lower()
        if any(word in name for word in ['hardcore', 'ssf', 'ruthless', 'solo self-found']):
            continue

        active_leagues.append(league)

    return active_leagues


active_leagues = get_current_leagues()
for league in active_leagues:
    print(f"{league['name']}")