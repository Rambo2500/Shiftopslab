from typing import Dict, Any, List


class RecoveryEngine:
    """
    Determines recovery horizon and shortfall metrics.
    """

    def __init__(self, recovery_rules: Dict[str, Any]):
        self.rules = recovery_rules

    def evaluate(self, timeline: List[Dict[str, Any]]) -> Dict[str, Any]:
        shortfall_days = 0
        max_shortfall = 0.0
        recovery_day_index = None

        for idx, day in enumerate(timeline):
            if day["shortfall"]:
                shortfall_days += 1
                max_shortfall = max(max_shortfall, day["shortfall_amount"])
            elif recovery_day_index is None:
                recovery_day_index = idx

        return {
            "recovery_horizon_days": recovery_day_index,
            "shortfall_days": shortfall_days,
            "max_shortfall_amount": round(max_shortfall, 2)
        }
