from engine.scenario_engine import ScenarioEngine
from scenarios.baseline_example import baseline_input
from scenarios.vegas_red_eye_example import vegas_input


def run():
    engine = ScenarioEngine(baseline_input)
    merged = engine.apply_scenario(vegas_input)

    # Baseline unchanged
    assert baseline_input != merged

    # Scenario overrides applied
    assert "one_time_events" in merged
    assert merged["one_time_events"] == vegas_input["one_time_events"]


if __name__ == "__main__":
    run()
