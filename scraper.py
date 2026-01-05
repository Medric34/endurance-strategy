import requests

def fetch_its_live():
    url = "https://api-live.its-live.net/v1/Session/GetRankingWithBestOfAll"

    payload = {
        "ssid": {
            "cs_id": "tte",
            "season": "2025",
            "event_id": "magnycoursfinale",
            "session_id": 23
        },
        "startPos": 1,
        "endPos": 99999999,
        "startId": 5891
    }

    headers = {
        "Content-Type": "application/json",
        "Origin": "https://www.its-live.net",
        "Referer": "https://www.its-live.net/"
    }

    r = requests.post(url, json=payload, headers=headers)
    return r.json()
