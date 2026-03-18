from typing import Dict, Any
import copy


class ScenarioEngine:
    """
    Applies scenario input on top of baseline input.
    No mutation of baseline.
    """

    def __init__(self, baseline_input: Dict[str, Any]):
        self.baseline = baseline_input

    def apply_scenario(self, scenario_input: Dict[str, Any]) -> Dict[str, Any]:
        merged = copy.deepcopy(self.baseline)

        for key, value in scenario_input.items():
            if key == "identifier":
                continue
            merged[key] = value

        return merged
