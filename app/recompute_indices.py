
import statistics as stats
from db import get_conn

def recompute_for_session(session_id: str):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
          SELECT car_id, lap_time_ms
          FROM laps WHERE session_id=%s AND pit=false AND fcy=false AND sc=false
        """, (session_id,))
        data = {}
        for car_id, lap_ms in cur.fetchall():
            data.setdefault(car_id, []).append(lap_ms)

        means = sorted([stats.mean(v) for v in data.values() if len(v)>=5])
        ref = stats.median(means[:3]) if means[:3] else None

        for car_id, laps in data.items():
            if not laps or not ref:
                continue
            pace = (stats.mean(laps) / ref - 1.0) * 100.0  # Δ% vs top3
            with conn.cursor() as c2:
                c2.execute("""
                  INSERT INTO indices(session_id, car_id, key, value)
                  VALUES (%s,%s,'PI_race',%s)
                  ON CONFLICT (session_id, car_id, key) DO UPDATE
                  SET value=EXCLUDED.value, updated_at=now()
                """, (session_id, car_id, round(pace,2)))

def main():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT DISTINCT session_id FROM final_classification""")
        for (sid,) in cur.fetchall():
            recompute_for_session(sid)

if __name__ == "__main__":
    main()

