"""
Loads existing real CSVs into Postgres, matching the schema in database/models.py.
"""
import sys
sys.path.append(".")
import pandas as pd
from database.base import SessionLocal
from database.models import District, Infrastructure, DisasterHistory
from utils.features import add_historical_rainfall_context, add_infrastructure_ratio

db = SessionLocal()

# --- Districts ---
districts_df = pd.read_csv("data/raw/districts.csv")
db.query(District).delete()  # clear on re-run, so this script is safely repeatable
for _, row in districts_df.iterrows():
    db.add(District(
        district_id=int(row.district_id), district_name=row.district_name,
        state=row.state, latitude=row.latitude, longitude=row.longitude,
        population=int(row.population),
    ))

# --- Infrastructure ---
infra_df = pd.read_csv("data/raw/infrastructure.csv")
db.query(Infrastructure).delete()
for _, row in infra_df.iterrows():
    db.add(Infrastructure(
        district_id=int(row.district_id), hospitals=int(row.hospitals),
        shelters=int(row.shelters), roads=int(row.roads),
        rescue_centers=int(row.rescue_centers),
    ))

# --- Disaster history (with engineered features already computed) ---
disasters_df = pd.read_csv("data/raw/disaster_history_real.csv")
for col in ["actual_rainfall_in_mm", "normal_rainfall_in_mm", "no_of_landslides", "population"]:
    disasters_df[col] = pd.to_numeric(disasters_df[col], errors="coerce")
disasters_df = disasters_df.dropna()
disasters_df = add_historical_rainfall_context(disasters_df, "data/raw/rainfall_india.csv")

db.query(DisasterHistory).delete()
for _, row in disasters_df.iterrows():
    db.add(DisasterHistory(
        district_id=int(row.district_id),
        actual_rainfall_in_mm=row.actual_rainfall_in_mm,
        normal_rainfall_in_mm=row.normal_rainfall_in_mm,
        no_of_landslides=int(row.no_of_landslides),
        full_damaged_houses=int(row.full_damaged_houses),
        fatalities=int(row.fatalities),
        severity=row.severity,
        rainfall_pct_of_normal=row.rainfall_pct_of_normal,
        rainfall_deviation_from_normal=row.rainfall_deviation_from_normal,
    ))

db.commit()
print(f"Loaded {len(districts_df)} districts, {len(infra_df)} infrastructure rows, {len(disasters_df)} disaster records.")
db.close()