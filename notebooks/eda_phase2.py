import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

Path("docs/eda_plots").mkdir(parents=True, exist_ok=True)

disasters = pd.read_csv("data/raw/disaster_history_real.csv")
print(disasters.describe())
print("\nSeverity distribution:\n", disasters["severity"].value_counts())

# Rainfall vs damage
plt.figure(figsize=(8, 5))
sns.scatterplot(data=disasters, x="actual_rainfall_in_mm", y="full_damaged_houses", hue="severity")
plt.title("Rainfall vs. Houses Damaged (Kerala 2018)")
plt.savefig("docs/eda_plots/rainfall_vs_damage.png")
plt.close()

# Correlation heatmap
numeric_cols = disasters.select_dtypes(include="number")
plt.figure(figsize=(8, 6))
sns.heatmap(numeric_cols.corr(), annot=True, cmap="coolwarm")
plt.title("Feature Correlations")
plt.savefig("docs/eda_plots/correlation_heatmap.png")
plt.close()

print("\nPlots saved to docs/eda_plots/")