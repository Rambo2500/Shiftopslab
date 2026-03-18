from typing import Dict, Any, List


class ConstraintEngine:
    """
    Applies priority classification to timeline outputs.
    Does NOT modify balances.
    """

    def __init__(self, constraint_schema: Dict[str, Any]):
        self.priority_order = constraint_schema["priority_order"]

    def apply(self, timeline: List[Dict[str, Any]], obligations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        obligation_priority = {
            ob["name"]: ob["category"] for ob in obligations
        }

        for day in timeline:
            day["priority_tags"] = []

            for name, category in obligation_priority.items():
                day["priority_tags"].append({
                    "name": name,
                    "category": category,
                    "priority_index": self._priority_index(category)
                })

        return timeline

    def _priority_index(self, category: str) -> int:
        try:
            return self.priority_order.index(category)
        except ValueError:
            return len(self.priority_order)

