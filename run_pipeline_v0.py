"""
Entry point: loads data, wires the orchestrator with concrete
implementations, runs the full cycle, prints results.
"""

import pandas as pd
import sys

sys.path.append(".")

from utils.features import add_historical_rainfall_context, add_infrastructure_ratio
from services.prediction_service import RuleBasedPredictor
from services.optimization_service import LPOptimizer
from pipeline.orchestrator import PipelineOrchestrator

# --- Load and engineer data ---
disasters = pd.read_csv("data/raw/disaster_history_real.csv")
for col in [
    "actual_rainfall_in_mm",
    "normal_rainfall_in_mm",
    "no_of_landslides",
    "population",
]:
    disasters[col] = pd.to_numeric(disasters[col], errors="coerce")
disasters = disasters.dropna()
disasters = add_historical_rainfall_context(disasters, "data/raw/rainfall_india.csv")
disasters = add_infrastructure_ratio(disasters, "data/raw/infrastructure.csv")
infra = pd.read_csv("data/raw/infrastructure.csv")


if __name__ == "__main__":
    orchestrator = PipelineOrchestrator(
        predictor=RuleBasedPredictor(),
        optimizer=LPOptimizer(),
        total_food_available=5000,
    )
    results = orchestrator.run_full_cycle(disasters, infra)

    for entry in results["district_results"]:
        print(f"\nDistrict: {entry['district']}")
        if "error" in entry:
            print(f"  ERROR: {entry['error']}")
            continue
        print(f"  Prediction: {entry['prediction']}")
        print(f"  Decision: {entry['decision']}")
        if "forecast" in entry:
            print(f"  Forecast: {entry['forecast']}")
            print(f"  Priority: {entry['priority']}")

    if results["allocation"]:
        print("\n--- Allocation Plan ---")
        print(f"Status: {results['allocation']['status']}")
        print(f"Allocation: {results['allocation']['allocation']}")
    else:
        print("\nNo districts flagged for optimization.")
