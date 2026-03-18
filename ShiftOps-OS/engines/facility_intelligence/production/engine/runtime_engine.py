import pandas as pd

def build_runtime_summary(schedule):
    """
    Builds runtime analytics from the Production Schedule.
    """
    df = schedule.copy()
    
    # Calculate duration in hours
    df["runtime_hours"] = (
        df["scheduled_end"] - df["scheduled_start"]
    ).dt.total_seconds() / 3600
    
    # Identify overlaps (simple check)
    df = df.sort_values(by=["line", "scheduled_start"])
    df["previous_end"] = df.groupby("line")["scheduled_end"].shift(1)
    df["overlap_warning"] = df["scheduled_start"] < df["previous_end"]
    
    return df
