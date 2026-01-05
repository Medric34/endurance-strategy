
# app/worker_finished.py
import os, json, time, uuid, requests
from psycopg2.extras import execute_values
from db import get_conn

SCREEN_UUID = os.getenv("SCREEN_UUID") or "e1658cae-5b86-4a7f-93d3-0eaa57ed0752"  # le tien ou un généré

BASE_HEADERS = {
    "Accept": "*/*",
    "Content-Type": "application/json; charset=utf-8",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "User-Agent": "Mozilla/5.0 (endurance-strategy-bot; +https://your-site)",
    "Referer": "https://www.its-live.net/",
    "X-Screen-UUID": SCREEN_UUID,
}

def fetch_ranking_post(url, body: dict, headers=None):
    h = dict(BASE_HEADERS)
    if headers:
        h.update(headers)
    r = requests.post(url, headers=h, json=body, timeout=25)
    r.raise_for_status()
    return r.json()

def store_session_boa(session_id, payload):
    boa = payload.get("boa")
    sboa = payload.get("sboa")
    boa_time = payload.get("boaTime")
    boa_time_lap = payload.get("boaTimeLap")
    if boa is None and sboa is None and boa_time is None and boa_time_lap is None:
        return
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
          INSERT INTO session_boa(session_id, boa, sboa, boa_time, boa_time_lap)
          VALUES (%s, %s::jsonb, %s::jsonb, %s, %s)
          ON CONFLICT (session_id) DO UPDATE
          SET boa=EXCLUDED.boa, sboa=EXCLUDED.sboa,
              boa_time=EXCLUDED.boa_time, boa_time_lap=EXCLUDED.boa_time_lap
        """, (session_id, json.dumps(boa), json.dumps(sboa), boa_time, boa_time_lap))

def store_ranking(session_id, payload):
    cars, bests = [], []

    for item in payload.get("ranking", []):
        car_id   = str(item.get("competitor_id") or item.get("number") or "")
        number   = item.get("number")
        pos      = item.get("pos")
        klass    = item.get("class") or item.get("cat")
        team     = item.get("team")
        brand    = item.get("brand")
        vehicle  = item.get("vehicle")
        total_lap= item.get("total_lap")

        dn = item.get("driver_names") or []
        drivers = ", ".join([d for d in dn if d])

        best_time_ms   = item.get("best_time")
        best_time_lap  = item.get("best_time_lap")
        last_lap_time  = item.get("lap_time")
        gap_first      = item.get("gap_first")
        gap_prev       = item.get("gap_prev")

        cars.append((
            session_id, car_id, number, pos, klass, team, brand, vehicle,
            drivers, total_lap, best_time_ms, best_time_lap, last_lap_time,
            gap_first, gap_prev
        ))

        s1 = item.get("best_inter_1")
        s2 = item.get("best_inter_2")
        s3 = item.get("best_inter_3")
        s4 = item.get("best_inter_4")
        best = item.get("best_time")
        bests.append((session_id, car_id, s1, s2, s3, best, s4))

    with get_conn() as conn, conn.cursor() as cur:
        if cars:
            execute_values(cur, """
              INSERT INTO final_classification(
                session_id, car_id, number, pos, class, team, brand, vehicle,
                drivers, total_lap, bestlap_ms, bestlap_no, last_lap_time_ms,
                gap_first, gap_prev
              )
              VALUES %s
              ON CONFLICT (session_id, car_id) DO UPDATE
              SET number=EXCLUDED.number, pos=EXCLUDED.pos, class=EXCLUDED.class,
                  team=EXCLUDED.team, brand=EXCLUDED.brand, vehicle=EXCLUDED.vehicle,
                  drivers=EXCLUDED.drivers, total_lap=EXCLUDED.total_lap,
                  bestlap_ms=EXCLUDED.bestlap_ms, bestlap_no=EXCLUDED.bestlap_no,
                  last_lap_time_ms=EXCLUDED.last_lap_time_ms,
                  gap_first=EXCLUDED.gap_first, gap_prev=EXCLUDED.gap_prev
            """, cars)

        if bests:
            execute_values(cur, """
              INSERT INTO best_of_all(session_id, car_id, s1_ms, s2_ms, s3_ms, best_ms, extra_s4)
              VALUES %s
              ON CONFLICT (session_id, car_id) DO UPDATE
              SET s1_ms=EXCLUDED.s1_ms, s2_ms=EXCLUDED.s2_ms, s3_ms=EXCLUDED.s3_ms,
                  best_ms=EXCLUDED.best_ms, extra_s4=EXCLUDED.extra_s4
            """, bests)

def main():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT session_id, url, params_json, body_json FROM sessions_to_fetch WHERE fetched=false""")
        todo = cur.fetchall()

    for session_id, url, params_json, body_json in todo:
        try:
            body = json.loads(body_json or "{}")
            payload = fetch_ranking_post(url, body=body)
            try:
                store_session_boa(session_id, payload)
            except Exception as e:
                print("session_boa skipped:", e)

            store_ranking(session_id, payload)

            with get_conn() as conn, conn.cursor() as cur:
                cur.execute("""UPDATE sessions_to_fetch SET fetched=true WHERE session_id=%s""", (session_id,))
        except Exception as e:
            print("ingestion error:", session_id, e)
            time.sleep(2)

if __name__ == "__main__":
    main()
