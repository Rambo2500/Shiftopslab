import sys
from pathlib import Path

# Ensure project root is on Python path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from run_pipeline import run_pipeline


def test_pipeline_end_to_end():
    output = run_pipeline(
        baseline_path="scenarios/baseline_example.json",
        scenario_path="scenarios/vegas_red_eye_example.json",
    )

    # Output shape
    assert isinstance(output, dict)
    assert "timeline" in output
    assert "recovery" in output

    timeline = output["timeline"]
    recovery = output["recovery"]

    assert isinstance(timeline, list)
    assert len(timeline) > 0

    required_day_keys = {
        "date",
        "starting_balance",
        "income_in",
        "obligations_out",
        "essentials_out",
        "one_time_out",
        "ending_balance",
        "shortfall",
        "shortfall_amount",
        "priority_tags",
    }

    for day in timeline:
        assert required_day_keys.issubset(day.keys())
        assert day["shortfall_amount"] >= 0

    assert recovery["recovery_horizon_days"] >= 0
    assert recovery["shortfall_days"] >= 0
    assert recovery["max_shortfall_amount"] >= 0
