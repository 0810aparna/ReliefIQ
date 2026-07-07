"""
Reusable feature engineering functions — imported by both training code
and (later) serving code, so they never diverge.
"""

import pandas as pd


def add_historical_rainfall_context(
    disasters: pd.DataFrame, rainfall_path: str
) -> pd.DataFrame:
    """
    Adds Kerala's long-term average monsoon (Jun-Sep) rainfall as a feature,
    and how much the 2018 actual rainfall deviated from that historical norm.
    This brings real multi-year signal into an otherwise single-season dataset.
    """
    rainfall = pd.read_csv(rainfall_path)
    kerala_rainfall = rainfall[rainfall["SUBDIVISION"].str.upper() == "KERALA"]

    historical_avg_monsoon = kerala_rainfall["Jun-Sep"].mean()

    disasters = disasters.copy()
    disasters["historical_avg_monsoon_rainfall"] = historical_avg_monsoon
    disasters["rainfall_deviation_from_normal"] = (
        disasters["actual_rainfall_in_mm"] - disasters["normal_rainfall_in_mm"]
    )
    disasters["rainfall_pct_of_normal"] = (
        disasters["actual_rainfall_in_mm"] / disasters["normal_rainfall_in_mm"]
    )
    return disasters


def add_infrastructure_ratio(disasters: pd.DataFrame, infra_path: str) -> pd.DataFrame:
    """Adds hospitals-per-capita as a feature, joining on district_id."""
    infra = pd.read_csv(infra_path)
    disasters = disasters.merge(infra, on="district_id", how="left")
    disasters["hospitals_per_100k"] = disasters["hospitals"] / (
        disasters["population"] / 100_000
    )
    return disasters
