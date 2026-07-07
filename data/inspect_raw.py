# data/inspect_raw.py
import pandas as pd
from pathlib import Path

raw_dir = Path("data/raw")

for csv_file in raw_dir.rglob("*.csv"):
    print(f"\n{'='*60}")
    print(f"FILE: {csv_file}")
    print("=" * 60)
    df = pd.read_csv(csv_file, nrows=5)
    print("Columns:", list(df.columns))
    print(df.head())
