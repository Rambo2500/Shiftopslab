import pandas as pd
from pathlib import Path

DIM_PATH = Path("dimensions/product_dimension.csv")


def load_product_dimension():
    df = pd.read_csv(DIM_PATH)

    df.columns = df.columns.str.strip().str.lower()

    # Mapping based on Product Dimension Table
    df = df.rename(
        columns={
            "fg oracle ref": "fg_oracle_ref",
            "fg legacy ref": "fg_legacy_ref",
            "unit ref": "unit_ref",
            "line": "line",
            "dough ref": "dough_ref",
        }
    )

    # Convert refs to strings and remove whitespace
    df["fg_oracle_ref"] = df["fg_oracle_ref"].astype(str).str.strip()
    df["fg_legacy_ref"] = df["fg_legacy_ref"].astype(str).str.strip()
    df["unit_ref"] = df["unit_ref"].astype(str).str.strip()

    # Drop rows without a valid SKU
    df = df.dropna(subset=["fg_oracle_ref"])
    df = df[df["fg_oracle_ref"] != "nan"]

    return df
