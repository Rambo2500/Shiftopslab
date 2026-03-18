from typing import Dict, Any, List
from datetime import datetime


class CheckerEngine:
    """
    Validates input data against checker_rules.json.
    Hard-fails on error conditions.
    """

    def __init__(self, checker_rules: Dict[str, Any]):
        self.rules = checker_rules["validation_rules"]

    def validate_inputs(self, input_data: Dict[str, Any]) -> None:
        errors: List[str] = []

        # CHK001: monetary values >= 0
        for src in input_data.get("income_sources", []):
            if src["amount"] < 0:
                errors.append("Income amount cannot be negative")

        for ob in input_data.get("fixed_obligations", []):
            if ob["amount"] < 0:
                errors.append("Fixed obligation amount cannot be negative")

        for ve in input_data.get("variable_essentials", []):
            if ve["estimated_amount"] < 0:
                errors.append("Variable essential amount cannot be negative")

        for evt in input_data.get("one_time_events", []):
            if evt["amount"] < 0:
                errors.append("One-time event amount cannot be negative")

        # CHK002: valid dates
        self._check_date(input_data.get("start_date"), errors)

        for src in input_data.get("income_sources", []):
            self._check_date(src.get("next_payment_date"), errors)

        for ob in input_data.get("fixed_obligations", []):
            self._check_date(ob.get("due_date"), errors)

        for evt in input_data.get("one_time_events", []):
            self._check_date(evt.get("date"), errors)

        # CHK003: planning_window_days > 0
        if input_data.get("planning_window_days", 0) <= 0:
            errors.append("planning_window_days must be greater than 0")

        # CHK004: frequency enums
        allowed_income_freq = {"weekly", "biweekly", "monthly", "irregular"}
        for src in input_data.get("income_sources", []):
            if src.get("frequency") not in allowed_income_freq:
                errors.append(f"Invalid income frequency: {src.get('frequency')}")

        allowed_var_freq = {"weekly", "monthly"}
        for ve in input_data.get("variable_essentials", []):
            if ve.get("frequency") not in allowed_var_freq:
                errors.append(f"Invalid variable essential frequency: {ve.get('frequency')}")

        if errors:
            raise ValueError({"checker_errors": errors})

    @staticmethod
    def _check_date(value: Any, errors: List[str]) -> None:
        try:
            datetime.fromisoformat(value)
        except Exception:
            errors.append(f"Invalid date format: {value}")

