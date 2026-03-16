import pandas as pd
from pathlib import Path

DATA_PATH = Path("data_raw/production_schedule.csv")

def load_schedule():
    """Loads the Production Schedule (Timeline)."""
    df = pd.read_csv(DATA_PATH)
    
    # Normalize column names for easier mapping
    df = df.rename(columns={
        "Line": "line",
        "Unit Ref": "unit_ref",
        "Start Time": "scheduled_start",
        "Finish Time": "scheduled_end",
        "Run Status": "status"
    })
    
    df["scheduled_start"] = pd.to_datetime(df["scheduled_start"])
    df["scheduled_end"] = pd.to_datetime(df["scheduled_end"])
    
    return df[["line", "unit_ref", "scheduled_start", "scheduled_end", "status"]]
