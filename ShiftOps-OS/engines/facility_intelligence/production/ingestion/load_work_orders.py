import pandas as pd
from pathlib import Path
import json

DATA_PATH = Path("data_raw/production_work_orders.csv")

def load_work_orders():
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip().str.lower()
    
    # Load column map
    with open("dimensions/column_map.json", "r") as f:
        col_map = json.load(f)["work_orders"]
    
    # Rename only found columns
    rename_dict = {k: v for k, v in col_map.items() if k in df.columns}
    df = df.rename(columns=rename_dict)

    df["date"] = pd.to_datetime(df["date"])
    
    # Optional columns if in MIPS
    if "production_date" in df.columns:
        df["production_date"] = pd.to_datetime(df["production_date"])
    
    df["sku"] = df["sku"].astype(str).str.strip()
    df["work_order_id"] = df["work_order_id"].astype(str).str.strip()
    
    # Numeric conversion
    df["booked_units"] = pd.to_numeric(df["booked_units"], errors="coerce").fillna(0)

    keep_cols = [col for col in ["date", "production_date", "line", "sku", "work_order_id", "booked_units"] if col in df.columns]
    return df[keep_cols]
