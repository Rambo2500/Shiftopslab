import pandas as pd
from pathlib import Path
import json

DATA_PATH = Path("data_raw/work_order_reconciliation.csv")

def load_receipts():
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip().str.lower()

    # Load column map
    with open("dimensions/column_map.json", "r") as f:
        col_map = json.load(f)["receipts"]

    # Rename based on map
    rename_dict = {k: v for k, v in col_map.items() if k in df.columns}
    df = df.rename(columns=rename_dict)

    if "received_ts" in df.columns:
        df["received_ts"] = pd.to_datetime(df["received_ts"])
        df["date"] = df["received_ts"].dt.normalize()
    
    df["sku"] = df["sku"].astype(str).str.strip()
    df["work_order_id"] = df["work_order_id"].astype(str).str.strip()
    
    # Numeric conversion
    df["received_units"] = pd.to_numeric(df["received_units"], errors="coerce").fillna(0)

    keep_cols = [col for col in ["date", "sku", "work_order_id", "received_units"] if col in df.columns]
    return df[keep_cols]
