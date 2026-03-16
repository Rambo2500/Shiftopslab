from engine.constraint_engine import ConstraintEngine
from engine.calculator_core import CalculatorCore
from contracts.constraint_schema import constraint_schema
from scenarios.baseline_example import baseline_input


def run():
    calc = CalculatorCore(baseline_input)
    timeline = calc.run()

    engine = ConstraintEngine(constraint_schema)
    constrained = engine.apply(timeline, baseline_input["fixed_obligations"])

    assert len(constrained) == len(timeline)

    for day in constrained:
        assert "priority_tags" in day
        assert isinstance(day["priority_tags"], list)


if __name__ == "__main__":
    run()
