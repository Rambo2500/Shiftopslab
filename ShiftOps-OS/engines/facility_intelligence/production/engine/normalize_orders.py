import pandas as pd

def normalize_orders(ordered: pd.DataFrame, dimension: pd.DataFrame) -> pd.DataFrame:
    """
    Normalizes orders by mapping legacy SKU to Oracle SKU.
    """
    if "fg_legacy_ref" in ordered.columns:
        ordered = ordered.merge(
            dimension[["fg_legacy_ref", "fg_oracle_ref"]],
            on="fg_legacy_ref",
            how="left"
        )
        ordered["sku"] = ordered["fg_oracle_ref"].fillna(ordered.get("sku", pd.NA))
        ordered = ordered.drop(columns=["fg_oracle_ref", "fg_legacy_ref"])
    return ordered
