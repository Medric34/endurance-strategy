
import os, psycopg2

DB_URL = os.getenv("DATABASE_URL")  # sera injectée par Render

def get_conn():
    return psycopg2.connect(DB_URL)

def init_db():
    with get_conn() as conn, conn.cursor() as cur:
        with open(os.path.join(os.path.dirname(__file__), "schema.sql"), "r") as f:
            cur.execute(f.read())

