import pandas as pd

def run_integrity_checks(truth_df):
    """
    Runs sanity checks on the truth table to catch operational anomalies.
    Returns a DataFrame of issues found.
    """
    issues = []

    for index, row in truth_df.iterrows():
        sku = row['sku']
        date = row['date']
        
        # 1. Under-booked (Demand > Booked)
        if row['ordered_units'] > row['booked_units']:
            issues.append({
                "Date": date,
                "SKU": sku,
                "Issue": "Under-booked",
                "Value": row['ordered_units'] - row['booked_units'],
                "Severity": "Warning"
            })
            
        # 2. Production Shortfall (Received < Booked)
        if row['received_units'] < row['booked_units']:
            issues.append({
                "Date": date,
                "SKU": sku,
                "Issue": "Production Shortfall",
                "Value": row['booked_units'] - row['received_units'],
                "Severity": "Warning"
            })
            
        # 3. Service Failure (Received < Ordered)
        if row['received_units'] < row['ordered_units']:
             issues.append({
                "Date": date,
                "SKU": sku,
                "Issue": "Service Failure (Shortage)",
                "Value": row['ordered_units'] - row['received_units'],
                "Severity": "Critical"
            })
             
        # 4. Excessive Overproduction (> 20% of orders)
        if row['ordered_units'] > 0:
            overprod_pct = (row['received_units'] - row['ordered_units']) / row['ordered_units']
            if overprod_pct > 0.20:
                issues.append({
                    "Date": date,
                    "SKU": sku,
                    "Issue": "Excessive Overproduction",
                    "Value": f"{overprod_pct:.1%}",
                    "Severity": "Info"
                })

    return pd.DataFrame(issues)
