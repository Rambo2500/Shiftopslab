import pandas as pd
import os

RATES_PATH = "dimensions/line_rates.csv"

def calculate_runtime(truth_table: pd.DataFrame) -> pd.DataFrame:
    """
    Estimates production runtime based on SKU rates and setup/cleanup constants.
    Formula: setup + (units / units_per_minute) + cleanup
    """
    if not os.path.exists(RATES_PATH):
        # Fallback to defaults if rates file is missing
        rates = pd.DataFrame(columns=["line", "sku", "units_per_minute", "setup_minutes", "cleanup_minutes"])
    else:
        rates = pd.read_csv(RATES_PATH)
        rates["sku"] = rates["sku"].astype(str)
        
    # Merge truth table with rates
    df = truth_table.copy()
    df["sku"] = df["sku"].astype(str)
    
    # We'll merge on sku and line if line is available, otherwise just sku
    merge_cols = ["sku"]
    if "line" in df.columns and "line" in rates.columns:
        merge_cols.append("line")
        
    df = df.merge(rates, on=merge_cols, how="left")
    
    # Fill defaults for missing mappings
    df["units_per_minute"] = df["units_per_minute"].fillna(300)
    df["setup_minutes"] = df["setup_minutes"].fillna(20)
    df["cleanup_minutes"] = df["cleanup_minutes"].fillna(10)
    
    # Run Calculation
    # We'll use planned_units as the target for runtime if booked_units isn't there
    target_col = "booked_units" if "booked_units" in df.columns else "planned_units"
    df["run_only_minutes"] = df[target_col] / df["units_per_minute"]
    df["runtime_minutes"] = df["setup_minutes"] + df["run_only_minutes"] + df["cleanup_minutes"]
    df["runtime_hours"] = df["runtime_minutes"] / 60
    
    return df
