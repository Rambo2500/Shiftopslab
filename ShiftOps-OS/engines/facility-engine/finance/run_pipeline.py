"""
Penny Pincher – Deterministic Execution Pipeline

This file is the single authoritative execution spine.
All consumers (tests, UI, CI, Android) call THIS.
No business logic lives here.
"""

import json
from pathlib import Path

from engine.scenario_engine import ScenarioEngine
from engine.checker_engine import CheckerEngine
from engine.calculator_core import CalculatorCore
from engine.constraint_engine import ConstraintEngine
from engine.recovery_engine import RecoveryEngine


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_pipeline(
    baseline_path: str,
    scenario_path: str | None = None,
):
    """
    Executes Penny Pincher end-to-end in deterministic order.

    Order (locked):
    1. Load baseline input
    2. Apply scenario overlay (optional)
    3. Validate inputs
    4. Calculate raw timeline
    5. Apply constraints
    6. Evaluate recovery
    7. Emit final output bundle
    """

    # --- Load contracts ---
    checker_rules = load_json("contracts/checker_rules.json")
    constraint_schema = load_json("contracts/constraint_schema.json")
    recovery_rules = load_json("contracts/recovery_rules.json")

    # --- Load baseline input ---
    baseline_input = load_json(baseline_path)

    # --- Apply scenario if provided ---
    if scenario_path:
        scenario_input = load_json(scenario_path)
        scenario_engine = ScenarioEngine(baseline_input)
        input_data = scenario_engine.apply_scenario(scenario_input)
    else:
        input_data = baseline_input

    # --- Validate inputs ---
    checker = CheckerEngine(checker_rules)
    checker.validate_inputs(input_data)

    # --- Calculate raw timeline ---
    calculator = CalculatorCore(input_data)
    timeline = calculator.run()

    # --- Apply constraints ---
    constraint_engine = ConstraintEngine(constraint_schema)
    constrained_timeline = constraint_engine.apply(
        timeline,
        input_data.get("fixed_obligations", []),
    )

    # --- Evaluate recovery ---
    recovery_engine = RecoveryEngine(recovery_rules)
    recovery_summary = recovery_engine.evaluate(constrained_timeline)

    # --- Final output ---
    return {
        "timeline": constrained_timeline,
        "recovery": recovery_summary,
    }


if __name__ == "__main__":
    # Example local run (safe default)
    output = run_pipeline(
        baseline_path="scenarios/baseline_example.json",
        scenario_path="scenarios/vegas_red_eye_example.json",
    )

    print(json.dumps(output, indent=2))
