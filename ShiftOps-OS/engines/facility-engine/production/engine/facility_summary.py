import pandas as pd

def generate_facility_summary(truth_df, detailed_orders):
    """
    Aggregates data by Facility (Location) to identify which lanes are driving risk.
    """
    if detailed_orders.empty:
        return pd.DataFrame()

    # Expand truth table back to locations using detailed_orders
    # Join on SKU and Date
    # detailed_orders has its own 'ordered_units'
    df = detailed_orders.merge(
        truth_df[["sku", "date", "service_risk", "labor_status"]],
        left_on=["sku", "sales_date"],
        right_on=["sku", "date"],
        how="inner"
    )
    
    # Define aggregation
    agg_map = {"ordered_units": "sum"}
    if "shipped_units" in df.columns: agg_map["shipped_units"] = "sum"
    if "received_units" in df.columns: agg_map["received_units"] = "sum"

    facility_stats = df.groupby("location").agg(agg_map).reset_index()
    
    # Calculate Fill Rate if shipped exists
    if "shipped_units" in facility_stats.columns:
        facility_stats["fill_rate_%"] = (facility_stats["shipped_units"] / facility_stats["ordered_units"].replace(0, 1) * 100).round(1)
    else:
        facility_stats["fill_rate_%"] = 0.0
    
    # Count Risks
    late_counts = df[df["service_risk"].str.contains("RED|YELLOW", na=False)].groupby("location").size().reset_index(name="late_runs")
    staffing_gaps = df[df["labor_status"].str.contains("PACKING|SHIPPING", na=False)].groupby("location").size().reset_index(name="staffing_gaps")
    
    # Merge counts
    facility_stats = facility_stats.merge(late_counts, on="location", how="left").fillna(0)
    facility_stats = facility_stats.merge(staffing_gaps, on="location", how="left").fillna(0)
    
    return facility_stats.sort_values("fill_rate_%")
