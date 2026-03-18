import pandas as pd
from datetime import datetime, timedelta

def generate_weekly_report(truth_df, roster_df=None):
    """
    Summarizes the truth table by Week for historical review.
    Calculates Fill Rate, Labor Capacity Utilization, and Service Metrics.
    """
    df = truth_df.copy()
    df["date"] = pd.to_datetime(df["date"])
    
    # Define the Week (Starting Sunday)
    df["week_start"] = df["date"].dt.to_period('W').apply(lambda r: r.start_time)
    
    # 1. Weekly Volume Metrics
    weekly_vol = df.groupby("week_start").agg({
        "ordered_units": "sum",
        "shipped_units": "sum",
        "received_units": "sum"
    }).reset_index()
    
    weekly_vol["fill_rate_%"] = (weekly_vol["shipped_units"] / weekly_vol["ordered_units"].replace(0, 1) * 100).round(1)
    
    # 2. Weekly Service Metrics
    def count_late(x): return sum("RED" in str(s) or "YELLOW" in str(s) for s in x)
    def count_staffing_gaps(x): return sum("PACKING" in str(s) or "SHIPPING" in str(s) for s in x)
    
    weekly_service = df.groupby("week_start").agg({
        "service_risk": count_late,
        "labor_status": count_staffing_gaps
    }).reset_index()
    weekly_service.columns = ["week_start", "late_runs", "staffing_gaps"]
    
    # 3. Weekly Labor Capacity (Hours)
    # If roster is provided, calculate total scheduled hours
    weekly_labor = pd.DataFrame()
    if roster_df is not None:
        roster = roster_df.copy()
        roster["start_time"] = pd.to_datetime(roster["start_time"])
        roster["end_time"] = pd.to_datetime(roster["end_time"])
        roster["hours"] = (roster["end_time"] - roster["start_time"]).dt.total_seconds() / 3600
        
        # Group by week (based on shift start date)
        roster["week_start"] = pd.to_datetime(roster["date"]).dt.to_period('W').apply(lambda r: r.start_time)
        weekly_labor = roster.groupby("week_start").agg({
            "hours": "sum",
            "name": "nunique"
        }).reset_index()
        weekly_labor.columns = ["week_start", "total_scheduled_hours", "headcount_count"]

    # Final Merge
    final_report = weekly_vol.merge(weekly_service, on="week_start", how="outer")
    if not weekly_labor.empty:
        final_report = final_report.merge(weekly_labor, on="week_start", how="outer")
    
    return final_report.sort_values("week_start", ascending=False)
