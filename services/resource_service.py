def forecast_resources(severity: str, population: int) -> dict:
    multiplier = {"Low": 0.02, "Medium": 0.05, "High": 0.15, "Critical": 0.30}[severity]
    affected = int(population * multiplier)
    return {
        "affected_population": affected,
        "food_packets": affected * 3,
        "medical_kits": int(affected * 0.1),
        "rescue_teams": max(1, affected // 5000),
    }
