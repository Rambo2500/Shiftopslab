from engine.calculator_core import CalculatorCore
from scenarios.baseline_example import baseline_input


def run():
    calc = CalculatorCore(baseline_input)
    timeline = calc.run()

    assert isinstance(timeline, list)
    assert len(timeline) == baseline_input["planning_window_days"]

    required_fields = {
        "date",
        "starting_balance",
        "income_in",
        "obligations_out",
        "essentials_out",
        "one_time_out",
        "ending_balance",
        "shortfall",
        "shortfall_amount",
    }

    for day in timeline:
        assert set(day.keys()) == required_fields
        assert isinstance(day["ending_balance"], float)

    # Determinism check
    timeline_2 = calc.run()
    assert timeline == timeline_2


if __name__ == "__main__":
    run()
