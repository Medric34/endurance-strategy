from fastapi import FastAPI
from scraper import fetch_its_live
from kpi import compute_kpi

app = FastAPI()

@app.get("/api/live")
def live():
    data = fetch_its_live()
    kpi = compute_kpi(data)
    return {
        "ranking": data,
        "kpi": kpi
    }
