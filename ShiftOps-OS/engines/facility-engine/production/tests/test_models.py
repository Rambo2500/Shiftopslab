import pandas as pd
from models.labor_model import calculate_labor_requirements
from models.runtime_model import calculate_runtime
from models.scheduler_model import optimize_schedule

def test_calculate_labor_requirements():
    df = pd.DataFrame({"booked_units": [1000, 2000, 500]})
    result = calculate_labor_requirements(df, units_per_worker_hour=500)
    assert "estimated_labor_hours" in result.columns
    assert list(result["estimated_labor_hours"]) == [2.0, 4.0, 1.0]

def test_calculate_runtime():
    df = pd.DataFrame({"booked_units": [2000, 4000, 1000]})
    result = calculate_runtime(df, units_per_hour=2000)
    assert "estimated_runtime_hours" in result.columns
    assert list(result["estimated_runtime_hours"]) == [1.0, 2.0, 0.5]

def test_optimize_schedule():
    df = pd.DataFrame({
        "line": ["B", "A", "A"],
        "production_date": ["2026-03-02", "2026-03-02", "2026-03-01"],
        "sku": ["1", "2", "1"],
        "booked_units": [100, 200, 300]
    })
    result = optimize_schedule(df)
    # Expected order: A/2026-03-01/1, A/2026-03-02/2, B/2026-03-02/1
    assert list(result["line"]) == ["A", "A", "B"]
    assert list(result["production_date"]) == ["2026-03-01", "2026-03-02", "2026-03-02"]
