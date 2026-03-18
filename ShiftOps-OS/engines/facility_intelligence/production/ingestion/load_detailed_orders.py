import pandas as pd
from pathlib import Path

DATA_PATH = Path("data_raw/detailed_orders.csv")

def load_detailed_orders():
    """Loads the detailed WMS order report with location data."""
    if not DATA_PATH.exists():
        return pd.DataFrame()

    df = pd.read_csv(DATA_PATH)
    
    # Map needed columns
    col_map = {
        "Destination Facility*": "location",
        "Item Code": "sku",
        "Current Ord Qty": "ordered_units",
        "Sales Date*": "sales_date"
    }
    
    # Keep only what we have
    found_cols = {k: v for k, v in col_map.items() if k in df.columns}
    df = df.rename(columns=found_cols)
    
    # Clean up
    df["sales_date"] = pd.to_datetime(df["sales_date"])
    df["sku"] = df["sku"].astype(str).str.strip()
    df["ordered_units"] = pd.to_numeric(df["ordered_units"], errors="coerce").fillna(0)
    
    return df[list(found_cols.values())]
