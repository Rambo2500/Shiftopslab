import pandas as pd
from pathlib import Path
import json

DATA_PATH = Path("data_raw/oasis_orders.csv")

def load_orders():
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip().str.lower()

    # Load column map
    with open("dimensions/column_map.json", "r") as f:
        col_map = json.load(f)["orders"]

    # Rename based on map
    rename_dict = {k: v for k, v in col_map.items() if k in df.columns}
    df = df.rename(columns=rename_dict)

    df["date"] = pd.to_datetime(df["date"])
    
    # Check for legacy ref if needed for SKU mapping
    if "fg_legacy_ref" in df.columns:
        df["fg_legacy_ref"] = df["fg_legacy_ref"].astype(str).str.strip()
    
    # Numeric conversion
    df["ordered_units"] = pd.to_numeric(df["ordered_units"], errors="coerce").fillna(0)

    # Filter to needed columns
    keep_cols = [col for col in ["date", "fg_legacy_ref", "sku", "ordered_units"] if col in df.columns]
    return df[keep_cols]
