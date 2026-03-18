import pandas as pd
from pathlib import Path
import json

DATA_PATH = Path("data_raw/production_work_orders.csv")

def load_production():
    """Loads Planned Production (Work Orders)."""
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip().str.lower()
    
    with open("dimensions/column_map.json", "r") as f:
        col_map = json.load(f)["work_orders"]
    
    rename_dict = {k: v for k, v in col_map.items() if k in df.columns}
    df = df.rename(columns=rename_dict)

    df["date"] = pd.to_datetime(df["date"])
    df["sku"] = df["sku"].astype(str).str.strip()
    df["planned_units"] = pd.to_numeric(df["booked_units"], errors="coerce").fillna(0)
    
    # Filter to available columns
    keep_cols = ["date", "sku", "planned_units"]
    if "line" in df.columns:
        keep_cols.append("line")
    
    return df[keep_cols]
