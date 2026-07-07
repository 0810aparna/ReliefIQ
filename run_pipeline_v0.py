"""
Full pipeline: rule-based severity prediction (ADR-008) -> decision engine
-> resource forecast -> priority-weighted, constrained optimization (Phase 3).
"""
import pandas as pd
from pathlib import Path
import sys
sys.path.append(".")
from utils.features import add_historical_rainfall_context, add_infrastructure_ratio
from services.rule_based_predictor import predict_severity_rule
from services.priority_service import compute_priority_score
from optimization.allocator import optimize_allocation_v2

# --- Load and engineer ---
disasters = pd.read_csv("data/raw/disaster_history_real.csv")
for col in ["actual_rainfall_in_mm", "normal_rainfall_in_mm", "no_of_landslides", "population"]:
    disasters[col] = pd.to_numeric(disasters[col], errors="coerce")
disasters = disasters.dropna()
disasters = add_historical_rainfall_context(disasters, "data/raw/rainfall_india.csv")
disasters = add_infrastructure_ratio(disasters, "data/raw/infrastructure.csv")

infra = pd.read_csv("data/raw/infrastructure.csv")


def decide_action(prediction: dict) -> dict:
    if prediction["severity"] in ("Critical",):
        return {"action": "RUN_OPTIMIZER", "alert_level": "Critical"}
    elif prediction["severity"] == "High":
        return {"action": "RUN_OPTIMIZER", "alert_level": "High"}
    else:
        return {"action": "MONITOR_ONLY", "alert_level": "Low"}


def forecast_resources(severity: str, population: int) -> dict:
    multiplier = {"Low": 0.02, "Medium": 0.05, "High": 0.15, "Critical": 0.30}[severity]
    affected = int(population * multiplier)
    return {"affected_population": affected, "food_packets": affected * 3,
            "medical_kits": int(affected * 0.1), "rescue_teams": max(1, affected // 5000)}


if __name__ == "__main__":
    demands, priorities, shelter_caps, transport_limits = {}, {}, {}, {}

    for _, row in disasters.iterrows():
        prediction = predict_severity_rule(
            rainfall_pct_of_normal=row.rainfall_pct_of_normal,
            no_of_landslides=row.no_of_landslides,
            rainfall_deviation_from_normal=row.rainfall_deviation_from_normal,
        )
        decision = decide_action(prediction)
        print(f"\nDistrict: {row.district_name}")
        print(f"  Prediction: {prediction}")
        print(f"  Decision: {decision}")

        if decision["action"] == "RUN_OPTIMIZER":
            forecast = forecast_resources(prediction["severity"], row.population)
            print(f"  Forecast: {forecast}")

            infra_row = infra[infra.district_id == row.district_id].iloc[0]
            priority = compute_priority_score(
                risk_score=prediction["risk_score"],
                population=row.population,
                hospitals=infra_row.hospitals,
                roads=infra_row.roads,
            )
            demands[row.district_id] = forecast["food_packets"]
            priorities[row.district_id] = priority
            shelter_caps[row.district_id] = infra_row.shelters * 1000       # illustrative: capacity per shelter
            transport_limits[row.district_id] = infra_row.roads * 50        # illustrative: delivery capacity per road-unit
            print(f"  Priority score: {priority}")

    if demands:
        print("\n--- Running priority-weighted, constrained allocation optimizer ---")
        result = optimize_allocation_v2(
            demands, priorities, shelter_caps, transport_limits, total_food_available=5000
        )
        print("Status:", result["status"])
        print("Allocation plan:", result["allocation"])
    else:
        print("\nNo districts flagged for optimization in this run.")