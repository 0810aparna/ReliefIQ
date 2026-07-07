import pandas as pd
import numpy as np
from collections import Counter
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneOut, GridSearchCV
from sklearn.metrics import accuracy_score, f1_score
import shap
import matplotlib.pyplot as plt
import joblib
import csv
from pathlib import Path
from datetime import datetime

import sys

sys.path.append(".")
from utils.features import add_historical_rainfall_context, add_infrastructure_ratio

# --- Load and engineer features ---
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

features = [
    "actual_rainfall_in_mm",
    "normal_rainfall_in_mm",
    "no_of_landslides",
    "population",
    "rainfall_deviation_from_normal",
    "rainfall_pct_of_normal",
    "hospitals_per_100k",
]
label_map = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}
reverse_map = {v: k for k, v in label_map.items()}

X = disasters[features]
y = disasters["severity"].map(label_map)

loo = LeaveOneOut()  # <-- defined ONCE here, reused everywhere below

# --- 4-class LOOCV ---
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

# --- Baseline check ---
majority_class = Counter(y).most_common(1)[0]
baseline_accuracy = majority_class[1] / len(y)
print(f"\nMajority-class baseline accuracy (4-class): {baseline_accuracy:.2f}")
print(f"Your model's LOOCV accuracy:                  {loocv_accuracy:.2f}")

# --- Binary collapse ---
disasters["severity_binary"] = disasters["severity"].map(
    {"Low": 0, "Medium": 0, "High": 1, "Critical": 1}
)
y_binary = disasters["severity_binary"]
baseline_binary = Counter(y_binary).most_common(1)[0][1] / len(y_binary)
print(f"\nBinary majority-class baseline: {baseline_binary:.2f}")

fold_predictions_bin, fold_actuals_bin = [], []
for train_idx, test_idx in loo.split(X):
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y_binary.iloc[train_idx], y_binary.iloc[test_idx]
    fold_model = XGBClassifier(n_estimators=30, max_depth=2)
    fold_model.fit(X_train, y_train)
    pred = fold_model.predict(X_test)
    fold_predictions_bin.append(pred[0])
    fold_actuals_bin.append(y_test.values[0])

binary_loocv_accuracy = accuracy_score(fold_actuals_bin, fold_predictions_bin)
print(
    f"Binary LOOCV accuracy (full features): {binary_loocv_accuracy:.2f} (baseline: {baseline_binary:.2f})"
)

# --- Trimmed features ---
trimmed_features = ["actual_rainfall_in_mm", "rainfall_pct_of_normal", "population"]
X_trimmed = disasters[trimmed_features]

fold_predictions_trim, fold_actuals_trim = [], []
for train_idx, test_idx in loo.split(X_trimmed):
    X_train, X_test = X_trimmed.iloc[train_idx], X_trimmed.iloc[test_idx]
    y_train, y_test = y_binary.iloc[train_idx], y_binary.iloc[test_idx]
    fold_model = XGBClassifier(n_estimators=30, max_depth=2)
    fold_model.fit(X_train, y_train)
    pred = fold_model.predict(X_test)
    fold_predictions_trim.append(pred[0])
    fold_actuals_trim.append(y_test.values[0])

trimmed_loocv_accuracy = accuracy_score(fold_actuals_trim, fold_predictions_trim)
print(
    f"Trimmed-features binary LOOCV accuracy: {trimmed_loocv_accuracy:.2f} (baseline: {baseline_binary:.2f})"
)

# --- Logistic Regression, trimmed features ---
fold_predictions_lr, fold_actuals_lr = [], []
for train_idx, test_idx in loo.split(X_trimmed):
    X_train, X_test = X_trimmed.iloc[train_idx], X_trimmed.iloc[test_idx]
    y_train, y_test = y_binary.iloc[train_idx], y_binary.iloc[test_idx]
    lr_model = LogisticRegression(max_iter=1000)
    lr_model.fit(X_train, y_train)
    pred = lr_model.predict(X_test)
    fold_predictions_lr.append(pred[0])
    fold_actuals_lr.append(y_test.values[0])

lr_accuracy = accuracy_score(fold_actuals_lr, fold_predictions_lr)
print(
    f"Logistic Regression (trimmed) LOOCV accuracy: {lr_accuracy:.2f} (baseline: {baseline_binary:.2f})"
)

# --- Summary ---
print("\n--- Summary ---")
print(
    f"4-class XGBoost accuracy:            {loocv_accuracy:.2f}  (baseline {baseline_accuracy:.2f})"
)
print(
    f"Binary XGBoost, full features:       {binary_loocv_accuracy:.2f}  (baseline {baseline_binary:.2f})"
)
print(
    f"Binary XGBoost, trimmed features:    {trimmed_loocv_accuracy:.2f}  (baseline {baseline_binary:.2f})"
)
print(
    f"Binary Logistic Regression, trimmed: {lr_accuracy:.2f}  (baseline {baseline_binary:.2f})"
)

# --- Save whichever full-feature 4-class model, for now (registry keeps full history either way) ---
final_model = XGBClassifier(n_estimators=50, max_depth=3)
final_model.fit(X, y)
Path("models/saved").mkdir(parents=True, exist_ok=True)
joblib.dump(final_model, "models/saved/xgb_v1.pkl")

explainer = shap.TreeExplainer(final_model)
shap_values = explainer.shap_values(X)
Path("docs/eda_plots").mkdir(parents=True, exist_ok=True)
shap.summary_plot(shap_values, X, show=False)
plt.savefig("docs/eda_plots/shap_summary.png", bbox_inches="tight")
plt.close()

registry_path = Path("models/model_registry.csv")
new_row = {
    "model_name": "xgb_v1",
    "timestamp": datetime.now().isoformat(),
    "features": ";".join(features),
    "metric_name": "loocv_accuracy",
    "metric_value": round(loocv_accuracy, 4),
    "dataset_version": "v2_real_kerala_engineered",
}
write_header = not registry_path.exists()
with open(registry_path, "a", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=new_row.keys())
    if write_header:
        writer.writeheader()
    writer.writerow(new_row)

print("\nDone.")
