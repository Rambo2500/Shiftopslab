from engine.recovery_engine import RecoveryEngine
from engine.calculator_core import CalculatorCore
from contracts.recovery_rules import recovery_rules
from scenarios.vegas_red_eye_example import vegas_input


def run():
    calc = CalculatorCore(vegas_input)
    timeline = calc.run()

    engine = RecoveryEngine(recovery_rules)
    result = engine.evaluate(timeline)

    assert "recovery_horizon_days" in result
    assert "shortfall_days" in result
    assert "max_shortfall_amount" in result

    assert isinstance(result["shortfall_days"], int)
    assert isinstance(result["max_shortfall_amount"], float)


if __name__ == "__main__":
    run()
