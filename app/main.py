
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import get_conn, init_db
import os

WEBADOR_ORIGIN = os.getenv("WEBADOR_ORIGIN", "*")  # mets ton domaine en prod

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[WEBADOR_ORIGIN],
    allow_headers=["*"],
    allow_methods=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/api/indices/{session_id}")
def get_indices(session_id: str):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT car_id, key, value FROM indices WHERE session_id=%s""", (session_id,))
        rows = cur.fetchall()
    out = {}
    for car_id, key, value in rows:
        out.setdefault(car_id, {})[key] = float(value)
    return out

@app.get("/api/classification/{session_id}")
def get_classification(session_id: str):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT car_id, pos, class, team, drivers, bestlap_ms
            FROM final_classification WHERE session_id=%s
            ORDER BY pos NULLS LAST
        """, (session_id,))
        rows = cur.fetchall()
    return [
        {"car": r[0], "pos": r[1], "class": r[2], "team": r[3], "drivers": r[4], "bestlap_ms": r[5]}
        for r in rows
    ]

