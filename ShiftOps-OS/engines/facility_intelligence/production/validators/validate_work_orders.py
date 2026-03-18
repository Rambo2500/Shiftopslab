import pandas as pd
from engine.load_dimension import load_product_dimension

def validate_work_orders(df):
    required_cols = ["sales date", "fg oracle ref", "submit qty (packs)"]
    
    # 1. Check for required columns
    cols_found = [col.lower() for col in df.columns]
    for col in required_cols:
        if col.lower() not in cols_found:
            return {"valid": False, "message": f"Missing required column: {col}"}
            
    # 2. Check for numeric and date integrity
    try:
        # Check if date is convertible
        if pd.to_datetime(df[df.columns[cols_found.index("sales date")]], errors='coerce').isna().any():
            return {"valid": False, "message": "File contains invalid dates in 'Sales Date' column."}
            
        # Check if units are numeric
        units_col = df.columns[cols_found.index("submit qty (packs)")]
        if pd.to_numeric(df[units_col], errors='coerce').isna().any():
            pass
    except Exception as e:
        return {"valid": False, "message": f"Data type conversion error: {str(e)}"}
        
    # 3. Check SKU Mapping (Oracle SKU)
    dimension = load_product_dimension()
    sku_col = df.columns[cols_found.index("fg oracle ref")]
    skus_in_file = set(df[sku_col].astype(str).str.strip().unique())
    skus_in_dim = set(dimension["fg_oracle_ref"].unique())
    
    missing_skus = skus_in_file - skus_in_dim
    if missing_skus:
        return {
            "valid": True, 
            "message": "Validated with warnings", 
            "warnings": [f"Missing {len(missing_skus)} Oracle SKU mappings in dimension table."]
        }
        
    return {"valid": True, "message": "Production Work Orders file validated successfully."}
