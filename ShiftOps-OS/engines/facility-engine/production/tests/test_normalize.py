import pandas as pd
from engine.normalize_orders import normalize_orders
from engine.normalize_production import normalize_production
from engine.normalize_shipments import normalize_shipments

def test_normalize_orders():
    ordered = pd.DataFrame({
        "fg_legacy_ref": ["LEG1", "LEG2", "UNKNOWN"],
        "ordered_units": [100, 200, 50]
    })
    dimension = pd.DataFrame({
        "fg_legacy_ref": ["LEG1", "LEG2"],
        "fg_oracle_ref": ["ORC1", "ORC2"]
    })
    result = normalize_orders(ordered, dimension)
    
    assert "sku" in result.columns
    assert list(result["sku"].fillna("NaN")) == ["ORC1", "ORC2", "NaN"]
    assert "fg_legacy_ref" not in result.columns

def test_normalize_production():
    df = pd.DataFrame({"booked_units": [100, 200]})
    result = normalize_production(df)
    assert len(result) == 2

def test_normalize_shipments():
    df = pd.DataFrame({"shipped_units": [100, 200]})
    result = normalize_shipments(df)
    assert len(result) == 2
