import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import LeaveOneOut, GridSearchCV
from sklearn.metrics import accuracy_score, f1_score
import shap
import joblib
import csv
from pathlib import Path
from datetime import datetime

import sys
sys.path.append(".")
from utils.features import add_historical_rainfall_context, add_infrastructure_ratio

# --- Load and engineer features ---
disasters = pd.read_csv("data/raw/disaster_history_real.csv")
for col in ["actual_rainfall_in_mm", "normal_rainfall_in_mm", "no_of_landslides", "population"]:
    disasters[col] = pd.to_numeric(disasters[col], errors="coerce")
disasters = disasters.dropna()

disasters = add_historical_rainfall_context(disasters, "data/raw/rainfall_india.csv")
disasters = add_infrastructure_ratio(disasters, "data/raw/infrastructure.csv")

features = [
    "actual_rainfall_in_mm", "normal_rainfall_in_mm", "no_of_landslides",
    "population", "rainfall_deviation_from_normal", "rainfall_pct_of_normal",
    "hospitals_per_100k",
]
label_map = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}
reverse_map = {v: k for k, v in label_map.items()}

X = disasters[features]
y = disasters["severity"].map(label_map)

# --- Leave-One-Out Cross-Validation: appropriate for n=13 ---
# Each fold trains on 12 districts, tests on the 1 held out — repeated 13 times.
# This is the standard approach for very small datasets where a single train/
# test split would leave too little data on either side to be meaningful.
loo = LeaveOneOut()
fold_predictions, fold_actuals = [], []

for train_idx, test_idx in loo.split(X):
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    fold_model = XGBClassifier(n_estimators=50, max_depth=3)
    fold_model.fit(X_train, y_train)
    pred = fold_model.predict(X_test)
    fold_predictions.append(pred[0])
    fold_actuals.append(y_test.values[0])

loocv_accuracy = accuracy_score(fold_actuals, fold_predictions)
loocv_f1 = f1_score(fold_actuals, fold_predictions, average="weighted")
print(f"LOOCV accuracy (honest, out-of-fold): {loocv_accuracy:.2f}")
print(f"LOOCV weighted F1: {loocv_f1:.2f}")

# --- Small hyperparameter search (grid kept small given tiny dataset) ---
param_grid = {"max_depth": [2, 3, 4], "n_estimators": [30, 50, 80], "learning_rate": [0.05, 0.1, 0.2]}
grid = GridSearchCV(XGBClassifier(), param_grid, cv=LeaveOneOut(), scoring="accuracy")
grid.fit(X, y)
print(f"Best params: {grid.best_params_}")

# --- Final model, trained on ALL data (standard practice once evaluation is done) ---
final_model = XGBClassifier(**grid.best_params_)
final_model.fit(X, y)

Path("models/saved").mkdir(parents=True, exist_ok=True)
joblib.dump(final_model, "models/saved/xgb_v1.pkl")

# --- SHAP explainability ---
explainer = shap.TreeExplainer(final_model)
shap_values = explainer.shap_values(X)
Path("docs/eda_plots").mkdir(parents=True, exist_ok=True)
shap.summary_plot(shap_values, X, show=False)
import matplotlib.pyplot as plt
plt.savefig("docs/eda_plots/shap_summary.png", bbox_inches="tight")
plt.close()
print("SHAP summary plot saved.")

# --- Log to model registry ---
registry_path = Path("models/model_registry.csv")
new_row = {
    "model_name": "xgb_v1", "timestamp": datetime.now().isoformat(),
    "features": ";".join(features), "metric_name": "loocv_accuracy",
    "metric_value": round(loocv_accuracy, 4), "dataset_version": "v2_real_kerala_engineered",
}
write_header = not registry_path.exists()
with open(registry_path, "a", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=new_row.keys())
    if write_header:
        writer.writeheader()
    writer.writerow(new_row)

print("\nDone. Model v1 saved, registered, and explained.")