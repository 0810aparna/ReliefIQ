"""
Phase 1 vertical slice — proving the full idea works end to end on REAL
Kerala 2018 flood data (district_wise_details.csv: real rainfall in mm,
landslides, damage counts).
"""
import pandas as pd
from xgboost import XGBClassifier
import joblib
from pathlib import Path
import csv
from datetime import datetime
import pulp

# --- Load real data ---
disasters = pd.read_csv("data/raw/disaster_history_real.csv")

# --- Clean numeric columns (real government data can have blanks/odd values) ---
numeric_cols = ["actual_rainfall_in_mm", "normal_rainfall_in_mm", "no_of_landslides", "population"]
for col in numeric_cols:
    disasters[col] = pd.to_numeric(disasters[col], errors="coerce")
disasters = disasters.dropna(subset=numeric_cols)
print(f"Rows available for training: {len(disasters)}")

# --- Features and label (severity already derived in load_real_data.py from damaged houses) ---
features = ["actual_rainfall_in_mm", "normal_rainfall_in_mm", "no_of_landslides", "population"]
label_map = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}
reverse_map = {v: k for k, v in label_map.items()}

X = disasters[features]
y_encoded = disasters["severity"].map(label_map)

# --- Train baseline model (small dataset — this is expected and fine for Phase 1) ---
model = XGBClassifier(n_estimators=50, max_depth=3)
model.fit(X, y_encoded)
train_accuracy = model.score(X, y_encoded)
print(f"Baseline train accuracy: {train_accuracy:.2f}")

Path("models/saved").mkdir(parents=True, exist_ok=True)
joblib.dump(model, "models/saved/xgb_v0.pkl")

registry_path = Path("models/model_registry.csv")
new_row = {
    "model_name": "xgb_v0", "timestamp": datetime.now().isoformat(),
    "features": ";".join(features), "metric_name": "train_accuracy",
    "metric_value": round(train_accuracy, 4), "dataset_version": "v1_real_kerala_2018_district_level",
}
write_header = not registry_path.exists()
with open(registry_path, "a", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=new_row.keys())
    if write_header:
        writer.writeheader()
    writer.writerow(new_row)


def predict_severity(features_dict: dict) -> dict:
    row = pd.DataFrame([features_dict])[features]
    pred_code = model.predict(row)[0]
    proba = model.predict_proba(row)[0]
    return {"severity": reverse_map[pred_code], "confidence": float(max(proba))}


def decide_action(prediction: dict) -> dict:
    if prediction["severity"] == "Critical":
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


def optimize_allocation(demands: dict, total_food_available: int) -> dict:
    prob = pulp.LpProblem("FoodAllocation", pulp.LpMaximize)
    allocation_vars = {d: pulp.LpVariable(f"alloc_{d}", lowBound=0, upBound=need) for d, need in demands.items()}
    prob += pulp.lpSum(allocation_vars.values())
    prob += pulp.lpSum(allocation_vars.values()) <= total_food_available
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    return {d: v.varValue for d, v in allocation_vars.items()}


if __name__ == "__main__":
    demands = {}
    for _, row in disasters.iterrows():
        features_row = {c: row[c] for c in features}
        prediction = predict_severity(features_row)
        decision = decide_action(prediction)
        print(f"\nDistrict: {row.district_name}")
        print(f"  Prediction: {prediction}")
        print(f"  Decision: {decision}")
        if decision["action"] == "RUN_OPTIMIZER":
            forecast = forecast_resources(prediction["severity"], row.population)
            print(f"  Forecast: {forecast}")
            demands[row.district_id] = forecast["food_packets"]

    if demands:
        print("\n--- Running allocation optimizer ---")
        print("Allocation plan:", optimize_allocation(demands, total_food_available=5000))
    else:
        print("\nNo districts flagged for optimization in this run.")