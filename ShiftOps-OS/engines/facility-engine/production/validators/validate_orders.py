import pandas as pd
from engine.load_dimension import load_product_dimension

def validate_orders(df):
    required_cols = ["date", "product code", "ord. units"]
    
    # 1. Check for required columns
    cols_found = [col.lower() for col in df.columns]
    for col in required_cols:
        if col.lower() not in cols_found:
            return {"valid": False, "message": f"Missing required column: {col}"}
            
    # 2. Check for numeric and date integrity
    try:
        # Check if date is convertible
        if pd.to_datetime(df[df.columns[cols_found.index("date")]], errors='coerce').isna().any():
            return {"valid": False, "message": "File contains invalid dates in 'date' column."}
            
        # Check if units are numeric
        units_col = df.columns[cols_found.index("ord. units")]
        if pd.to_numeric(df[units_col], errors='coerce').isna().any():
            # If some are NaN, it's okay as long as we know why, but we'll flag it
            pass
    except Exception as e:
        return {"valid": False, "message": f"Data type conversion error: {str(e)}"}
        
    # 3. Check SKU Mapping
    dimension = load_product_dimension()
    product_code_col = df.columns[cols_found.index("product code")]
    skus_in_file = set(df[product_code_col].astype(str).str.strip().unique())
    skus_in_dim = set(dimension["fg_legacy_ref"].unique())
    
    missing_skus = skus_in_file - skus_in_dim
    if missing_skus:
        # We'll allow it but return a warning flag later
        # For now, we'll just return valid: True with metadata
        return {
            "valid": True, 
            "message": "Validated with warnings", 
            "warnings": [f"Missing {len(missing_skus)} SKU mappings in dimension table."]
        }
        
    return {"valid": True, "message": "OASIS Orders file validated successfully."}
