def compute_kpi(data):
    ranking = data.get("Ranking", [])

    if not ranking:
        return {}

    leader = ranking[0]

    return {
        "leader_last_lap": leader.get("LastLap"),
        "leader_best_lap": leader.get("BestLap"),
        "total_cars": len(ranking)
    }
