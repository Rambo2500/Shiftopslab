import pandas as pd
from datetime import datetime, timedelta

def optimize_schedule(labor_df: pd.DataFrame, default_shift_start_hour: int = 6) -> pd.DataFrame:
    """
    Sequences production runs on each line.
    Calculates start_time and end_time for each SKU run.
    """
    df = labor_df.copy()
    
    # Sort for deterministic sequencing
    sort_cols = [col for col in ["production_date", "line", "sku"] if col in df.columns]
    if not sort_cols:
        sort_cols = ["date", "sku"]
    df = df.sort_values(by=sort_cols).reset_index(drop=True)
    
    # Result container
    scheduled_runs = []
    
    # Track current end time for each line
    # key: line, value: last_end_time
    line_clocks = {}
    
    for _, row in df.iterrows():
        line = row.get("line", "Unknown Line")
        prod_date = row.get("production_date", row.get("date"))
        
        # Normalize prod_date to datetime if it's not already
        if not isinstance(prod_date, datetime):
            prod_date = pd.to_datetime(prod_date)
            # If it's still just a Timestamp, convert to datetime
            if hasattr(prod_date, "to_pydatetime"):
                prod_date = prod_date.to_pydatetime()
        
        # Initial shift start for the day on this line
        if line not in line_clocks:
            shift_start = prod_date.replace(hour=default_shift_start_hour, minute=0, second=0)
            line_clocks[line] = shift_start
            
        start_time = line_clocks[line]
        runtime_mins = row.get("runtime_minutes", 0)
        end_time = start_time + timedelta(minutes=float(runtime_mins))
        
        # Update clock for next run on this line
        line_clocks[line] = end_time
        
        # Create output row
        run_data = row.to_dict()
        run_data["start_time"] = start_time
        run_data["end_time"] = end_time
        scheduled_runs.append(run_data)
        
    return pd.DataFrame(scheduled_runs)
