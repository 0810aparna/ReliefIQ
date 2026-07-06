"""
Generates ONLY infrastructure data synthetically — the one field with no
accessible real public source. Scaled from real population figures.
"""
import numpy as np
import pandas as pd

np.random.seed(42)

districts = pd.read_csv("data/raw/district_population.csv")
districts["district_id"] = range(1, len(districts) + 1)

infra_rows = []
for _, d in districts.iterrows():
    infra_rows.append({
        "district_id": d.district_id,
        "hospitals": max(1, int(d.population / 150000 + np.random.randint(-1, 2))),
        "shelters": max(1, int(d.population / 80000 + np.random.randint(-1, 2))),
        "roads": np.random.randint(50, 300),
        "rescue_centers": np.random.randint(1, 6),
    })

pd.DataFrame(infra_rows).to_csv("data/raw/infrastructure.csv", index=False)
print(f"Generated synthetic infrastructure for {len(infra_rows)} districts.")
