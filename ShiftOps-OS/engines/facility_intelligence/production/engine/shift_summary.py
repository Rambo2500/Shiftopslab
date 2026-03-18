import pandas as pd
import os

def generate_shift_summary(truth_df):
    """
    Creates a summary for management highlighting Service Risks and Labor gaps.
    """
    # Filter for items that actually have a schedule
    summary = truth_df[truth_df["scheduled_start"].notna()].copy()
    
    # Select key columns for management
    cols = [
        "date", "sku", "service_risk", "labor_status", 
        "scheduled_start", "scheduled_end", "shipping_actual", "packing_actual"
    ]
    summary = summary[cols]
    
    # Add a 'Priority' flag for management
    def get_priority(row):
        sr = str(row["service_risk"])
        if "RED" in sr:
            return "CRITICAL: SYSTEM LATE"
        if "YELLOW" in sr:
            return "WARNING: INTERNAL RISK"
        if "PACKING" in str(row["labor_status"]) or "SHIPPING" in str(row["labor_status"]):
            return "HIGH: STAFFING GAP"
        return "NORMAL"
        
    summary["management_priority"] = summary.apply(get_priority, axis=1)
    
    # Sort by priority
    priority_map = {"CRITICAL: SYSTEM LATE": 0, "WARNING: INTERNAL RISK": 1, "HIGH: STAFFING GAP": 2, "NORMAL": 3}
    summary["p_val"] = summary["management_priority"].map(priority_map)
    summary = summary.sort_values("p_val").drop(columns=["p_val"])
    
    return summary
