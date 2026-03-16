from engine.checker_engine import CheckerEngine
from contracts.checker_rules import checker_rules
from scenarios.baseline_example import baseline_input


def run():
    checker = CheckerEngine(checker_rules)

    # Valid input should pass
    checker.validate_inputs(baseline_input)

    # Invalid input should fail
    bad = dict(baseline_input)
    bad["planning_window_days"] = 0

    try:
        checker.validate_inputs(bad)
        assert False, "Expected checker to fail on invalid planning_window_days"
    except ValueError as e:
        assert "planning_window_days" in str(e)


if __name__ == "__main__":
    run()
