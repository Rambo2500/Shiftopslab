import pandas as pd
from pathlib import Path
import json

DATA_PATH = Path("data_raw/wms_shipments.csv")

def load_shipments():
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip().str.lower()

    # Load column map
    with open("dimensions/column_map.json", "r") as f:
        col_map = json.load(f)["shipments"]

    # Rename based on map
    rename_dict = {k: v for k, v in col_map.items() if k in df.columns}
    df = df.rename(columns=rename_dict)

    # Filter out cancelled orders
    if "order stat" in df.columns:
        df = df[df["order stat"].str.lower() != "cancelled"]

    df["date"] = pd.to_datetime(df["date"])
    df["sku"] = df["sku"].astype(str).str.strip()
    
    # Force numeric conversion
    df["shipped_units"] = pd.to_numeric(df["shipped_units"], errors="coerce").fillna(0)

    keep_cols = [col for col in ["date", "sku", "shipped_units"] if col in df.columns]
    return df[keep_cols]
