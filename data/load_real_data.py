import pandas as pd
from pathlib import Path

RAW = Path("data/raw")

# --- Districts (real, Census-based) ---
districts = pd.read_csv(RAW / "district_population.csv")
districts["district_id"] = range(1, len(districts) + 1)
districts.to_csv(RAW / "districts.csv", index=False)

# --- Daily warnings data: real rainfall + real warning severity, many rows per district ---
warnings_df = pd.read_csv(RAW / "kerala_floods_2018" / "warnings_actual_predicted.csv")
warnings_df = warnings_df.rename(columns={"predicted_rainfall": "warning_level"})
warnings_df = warnings_df.merge(
    districts[["district_id", "district_name", "population"]],
    left_on="district", right_on="district_name", how="inner"
)
warnings_df.to_csv(RAW / "weather_real.csv", index=False)
print(f"weather_real.csv: matched {warnings_df.district_id.nunique()} districts, {len(warnings_df)} rows total")

# --- 2018 event summary per district (real, one row per district) ---
disaster_df = pd.read_csv(RAW / "kerala_floods_2018" / "district_wise_details.csv")
disaster_df = disaster_df.merge(
    districts[["district_id", "district_name", "population"]],
    left_on="district", right_on="district_name", how="inner"
)

def severity_from_damage(houses: int) -> str:
    if houses >= 2000: return "Critical"
    elif houses >= 500: return "High"
    elif houses >= 100: return "Medium"
    else: return "Low"

disaster_df["severity"] = disaster_df["full_damaged_houses"].apply(severity_from_damage)
disaster_df.to_csv(RAW / "disaster_history_real.csv", index=False)
print(f"disaster_history_real.csv: matched {disaster_df.district_id.nunique()} districts")
