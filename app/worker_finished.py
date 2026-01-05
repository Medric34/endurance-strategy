
import os, json, time, requests
from psycopg2.extras import execute_values
from db import get_conn

USER_AGENT = "Mozilla/5.0 (endurance-strategy-bot; +https://your-site)"
BASE_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://live.its-chronotiming.example/",  # adapte au domaine réel
}

def fetch_ranking(url, params=None, headers=None):
    h = dict(BASE_HEADERS)
    if headers:
        h.update(headers)
    r = requests.get(url, params=params or {}, headers=h, timeout=15)
    r.raise_for_status()
    return r.json()

def store_ranking(session_id, payload):
    cars, laps, bests = [], [], []

    # Adapte ces clés aux champs réels de la réponse JSON de GetRankingWithBestOfAll
    for item in payload.get("Ranking", []):
        car_id  = str(item.get("CarNumber") or item.get("Number") or "")
        pos     = item.get("Position")
        cls     = item.get("Class")
        bestlap = item.get("BestLapTimeMs")
        team    = item.get("TeamName")
        drivers = ",".join(item.get("Drivers", []))

        cars.append((session_id, car_id, pos, cls, team, drivers, bestlap))

        # Laps
        for lap in item.get("Laps", []):
            laps.append((
                session_id, car_id,
                lap.get("LapNo"), lap.get("LapTimeMs"),
                bool(lap.get("Pit")), bool(lap.get("FCY")), bool(lap.get("SC"))
            ))

        # BestOfAll
        b = item.get("BestOfAll", {})
        bests.append((
            session_id, car_id,
            b.get("S1Ms"), b.get("S2Ms"), b.get("S3Ms"),
            b.get("BestLapMs")
        ))

    with get_conn() as conn, conn.cursor() as cur:
        if cars:
            execute_values(cur, """
              INSERT INTO final_classification(session_id, car_id, pos, class, team, drivers, bestlap_ms)
              VALUES %s
              ON CONFLICT (session_id, car_id) DO UPDATE
              SET pos=EXCLUDED.pos, bestlap_ms=EXCLUDED.bestlap_ms, team=EXCLUDED.team, drivers=EXCLUDED.drivers, class=EXCLUDED.class
            """, cars)

        if laps:
            execute_values(cur, """
              INSERT INTO laps(session_id, car_id, lap_no, lap_time_ms, pit, fcy, sc)
              VALUES %s
              ON CONFLICT DO NOTHING
            """, laps)

        if bests:
            execute_values(cur, """
              INSERT INTO best_of_all(session_id, car_id, s1_ms, s2_ms, s3_ms, best_ms)
              VALUES %s
              ON CONFLICT (session_id, car_id) DO UPDATE
              SET s1_ms=EXCLUDED.s1_ms, s2_ms=EXCLUDED.s2_ms, s3_ms=EXCLUDED.s3_ms, best_ms=EXCLUDED.best_ms
            """, bests)

def main():
    # Récupère la liste des sessions non fetchées
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT session_id, url, params_json FROM sessions_to_fetch WHERE fetched=false""")
        todo = cur.fetchall()

    for session_id, url, params_json in todo:
        try:
            params = json.loads(params_json or "{}")
            payload = fetch_ranking(url, params=params)
            store_ranking(session_id, payload)
            with get_conn() as conn, conn.cursor() as cur:
                cur.execute("""UPDATE sessions_to_fetch SET fetched=true WHERE session_id=%s""", (session_id,))
        except Exception as e:
            print("ingestion error:", session_id, e)
            time.sleep(2)

if __name__ == "__main__":
    main()

