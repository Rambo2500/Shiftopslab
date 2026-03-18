import pandas as pd

def generate_control_tower(truth_df):
    """
    Generates a Control Tower summary focusing on Production vs Shipped.
    """
    df = truth_df.copy()
    
    # KPIs
    df["fill_rate_%"] = (df["shipped_units"] / df.replace(0, 1)["ordered_units"] * 100).round(1)
    df["prod_completion_%"] = (df["received_units"] / df.replace(0, 1)["planned_units"] * 100).round(1)
    
    # Control Tower Status
    def get_ct_status(row):
        if row["shipped_units"] < row["ordered_units"]:
            return "SHORT SHIP"
        if "RED" in str(row["service_risk"]):
            return "TIMING FAILURE"
        if "YELLOW" in str(row["service_risk"]):
            return "TIMING RISK"
        return "CLEAR"
        
    df["control_tower_status"] = df.apply(get_ct_status, axis=1)
    
    # Final Report Columns
    summary_cols = [
        "date", "sku", "ordered_units", "planned_units", "received_units", 
        "shipped_units", "fill_rate_%", "prod_completion_%", 
        "control_tower_status", "service_risk"
    ]
    
    return df[summary_cols]
