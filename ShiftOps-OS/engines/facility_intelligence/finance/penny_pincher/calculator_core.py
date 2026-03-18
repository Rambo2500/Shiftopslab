from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, List, Any, Tuple


def _iso_to_date(s: str) -> date:
    return datetime.fromisoformat(s).date()


def _date_to_iso(d: date) -> str:
    return d.isoformat()


def _add_months(d: date, months: int) -> date:
    """
    Deterministic month add:
    - Advances month by N
    - Clamps day to last valid day of target month
    """
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1

    # days per month
    if m in (1, 3, 5, 7, 8, 10, 12):
        last = 31
    elif m in (4, 6, 9, 11):
        last = 30
    else:
        # Feb leap year
        leap = (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0))
        last = 29 if leap else 28

    day = min(d.day, last)
    return date(y, m, day)


@dataclass(frozen=True)
class _LineDay:
    date: str
    starting_balance: float
    income_in: float
    obligations_out: float
    essentials_out: float
    one_time_out: float
    ending_balance: float
    shortfall: bool
    shortfall_amount: float

    def as_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date,
            "starting_balance": round(self.starting_balance, 2),
            "income_in": round(self.income_in, 2),
            "obligations_out": round(self.obligations_out, 2),
            "essentials_out": round(self.essentials_out, 2),
            "one_time_out": round(self.one_time_out, 2),
            "ending_balance": round(self.ending_balance, 2),
            "shortfall": self.shortfall,
            "shortfall_amount": round(self.shortfall_amount, 2),
        }


class CalculatorCore:
    """
    Responsible for timeline-based cashflow calculation.
    Consumes validated inputs.
    Produces raw timeline data only.
    """

    def __init__(self, input_data: Dict[str, Any]):
        self.input_data = input_data

    def run(self) -> List[Dict[str, Any]]:
        """
        Execute deterministic cashflow calculation.

        Returns:
            list[dict]: raw timeline structure (pre-constraints, pre-recovery)
        """
        start = _iso_to_date(self.input_data["start_date"])
        window_days = int(self.input_data["planning_window_days"])
        end = start + timedelta(days=window_days)

        # Expand into per-day totals (math only; no prioritization)
        income_map = self._expand_income(start, end)
        obligations_map = self._expand_fixed_obligations()
        essentials_map = self._expand_variable_essentials(start, end)
        one_time_map = self._expand_one_time_events()

        timeline: List[_LineDay] = []
        balance = 0.0

        for i in range(window_days):
            day = start + timedelta(days=i)
            key = _date_to_iso(day)

            income = income_map.get(key, 0.0)
            obligations = obligations_map.get(key, 0.0)
            essentials = essentials_map.get(key, 0.0)
            one_time = one_time_map.get(key, 0.0)

            starting_balance = balance
            ending_balance = starting_balance + income - obligations - essentials - one_time

            shortfall = ending_balance < 0
            shortfall_amount = abs(ending_balance) if shortfall else 0.0

            timeline.append(
                _LineDay(
                    date=key,
                    starting_balance=starting_balance,
                    income_in=income,
                    obligations_out=obligations,
                    essentials_out=essentials,
                    one_time_out=one_time,
                    ending_balance=ending_balance,
                    shortfall=shortfall,
                    shortfall_amount=shortfall_amount,
                )
            )

            balance = ending_balance

        return [d.as_dict() for d in timeline]

    # -----------------------------
    # Expansion helpers (still math)
    # -----------------------------

    def _expand_income(self, start: date, end: date) -> Dict[str, float]:
        """
        Expands income_sources into a date->amount map within [start, end).
        Supports weekly, biweekly, monthly, irregular.
        Irregular emits only the given next_payment_date once.
        """
        out: Dict[str, float] = {}

        for src in self.input_data["income_sources"]:
            amount = float(src["amount"])
            freq = str(src["frequency"])
            next_pay = _iso_to_date(src["next_payment_date"])

            current = next_pay
            while current < end:
                if current >= start:
                    k = _date_to_iso(current)
                    out[k] = out.get(k, 0.0) + amount

                if freq == "weekly":
                    current = current + timedelta(days=7)
                elif freq == "biweekly":
                    current = current + timedelta(days=14)
                elif freq == "monthly":
                    current = _add_months(current, 1)
                elif freq == "irregular":
                    break
                else:
                    # Unknown freq should be handled by checker; here we just stop.
                    break

        return out

    def _expand_fixed_obligations(self) -> Dict[str, float]:
        """
        fixed_obligations are already point-in-time due_date items.
        Map due_date -> sum(amount)
        """
        out: Dict[str, float] = {}

        for ob in self.input_data["fixed_obligations"]:
            k = str(ob["due_date"])
            amt = float(ob["amount"])
            out[k] = out.get(k, 0.0) + amt

        return out

    def _expand_variable_essentials(self, start: date, end: date) -> Dict[str, float]:
        """
        variable_essentials are estimated recurring outflows.

        Policy (simple, deterministic):
        - weekly: charge on start_date weekday each week
        - monthly: charge on start_date day-of-month (clamped by calendar via _add_months)
        """
        out: Dict[str, float] = {}

        window_days = (end - start).days

        for ve in self.input_data.get("variable_essentials", []):
            amt = float(ve["estimated_amount"])
            freq = str(ve["frequency"])

            if freq == "weekly":
                anchor_weekday = start.weekday()
                for i in range(window_days):
                    d = start + timedelta(days=i)
                    if d.weekday() == anchor_weekday:
                        k = _date_to_iso(d)
                        out[k] = out.get(k, 0.0) + amt

            elif freq == "monthly":
                # Emit on start day-of-month, and then each month after (within range)
                current = start
                while current < end:
                    k = _date_to_iso(current)
                    out[k] = out.get(k, 0.0) + amt
                    current = _add_months(current, 1)

            else:
                # Unknown freq should be handled by checker; ignore here.
                continue

        return out

    def _expand_one_time_events(self) -> Dict[str, float]:
        """
        one_time_events are point-in-time outflows.
        Map date -> sum(amount)
        """
        out: Dict[str, float] = {}

        for evt in self.input_data.get("one_time_events", []):
            k = str(evt["date"])
            amt = float(evt["amount"])
            out[k] = out.get(k, 0.0) + amt

        return out

