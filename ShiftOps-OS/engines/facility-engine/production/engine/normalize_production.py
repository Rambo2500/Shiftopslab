import pandas as pd

def normalize_production(production_df: pd.DataFrame, dimension_df: pd.DataFrame) -> pd.DataFrame:
    """
    Expands dough/unit runs into SKU-level production if needed.
    """
    df = production_df.copy()
    
    # If the input doesn't have 'sku' but has 'unit_ref' or 'dough_ref', expand it
    if "sku" not in df.columns:
        if "unit_ref" in df.columns:
            df = df.merge(
                dimension_df[["unit_ref", "fg_oracle_ref"]],
                on="unit_ref",
                how="left"
            ).rename(columns={"fg_oracle_ref": "sku"})
        elif "dough_ref" in df.columns:
            df = df.merge(
                dimension_df[["dough_ref", "fg_oracle_ref"]],
                on="dough_ref",
                how="left"
            ).rename(columns={"fg_oracle_ref": "sku"})
            
    # Ensure SKU is string and cleaned
    if "sku" in df.columns:
        df["sku"] = df["sku"].astype(str).str.strip()
        
    return df
