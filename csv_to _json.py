"""
Kaggle CSV -> JSON Converter
Manually download kiye datasets ko JSON mein convert karta hai
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

KAGGLE_DIR = Path("data/kaggle")
all_data = []

print("Converting CSV files to JSON...\n")

for csv_file in KAGGLE_DIR.rglob("*.csv"):
    try:
        df = pd.read_csv(csv_file, encoding="utf-8", on_bad_lines="skip")
        df = df.dropna(how="all")
        df.columns = [c.lower().replace(" ", "_") for c in df.columns]
        records = df.to_dict(orient="records")
        
        for r in records:
            r["_file"] = csv_file.name
            r["_scraped_at"] = datetime.now().isoformat()
        
        all_data.extend(records)
        
        # Alag JSON bhi save karo
        out = csv_file.with_suffix(".json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        
        print(f"+ {csv_file.name}: {len(records)} records -> {out.name}")
    
    except Exception as e:
        print(f"  Error {csv_file.name}: {e}")

# Master file
with open(KAGGLE_DIR / "all_kaggle_data.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)

print(f"\nDONE! Total: {len(all_data)} records")
print(f"Saved: data/kaggle/all_kaggle_data.json")