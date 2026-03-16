import pandas as pd
from engine.load_dimension import load_product_dimension

def validate_receipts(df):
    required_cols = ["received ts", "item", "work order nbr", "received qty"]
    
    # 1. Check for required columns
    cols_found = [col.lower() for col in df.columns]
    for col in required_cols:
        if col.lower() not in cols_found:
            return {"valid": False, "message": f"Missing required column: {col}"}
            
    # 2. Check for numeric and date integrity
    try:
        # Check if date is convertible
        if pd.to_datetime(df[df.columns[cols_found.index("received ts")]], errors='coerce').isna().any():
            return {"valid": False, "message": "File contains invalid dates in 'Received TS' column."}
            
        # Check if units are numeric
        units_col = df.columns[cols_found.index("received qty")]
        if pd.to_numeric(df[units_col], errors='coerce').isna().any():
            pass
    except Exception as e:
        return {"valid": False, "message": f"Data type conversion error: {str(e)}"}
        
    return {"valid": True, "message": "Work Order Reconciliation file validated successfully."}
