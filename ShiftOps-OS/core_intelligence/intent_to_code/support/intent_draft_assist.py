"""
Intent draft assist (read-only).

Uses Context Harvest artifacts to help a human
structure a draft intent.

This module:
- does NOT author intent
- does NOT validate
- does NOT execute
- does NOT infer decisions

Output is a suggestion scaffold only.
"""

from typing import Dict, List


def draft_intent_from_context(context: Dict) -> Dict:
    """
    Produce a non-authoritative intent draft scaffold
    from context observations.

    Human review is always required.
    """

    topic = context.get("topic", "")
    observations: List[str] = context.get("observations", [])
    constraints: List[str] = context.get("constraints", [])

    return {
        "goal_suggestion": topic,
        "considerations": observations,
        "known_constraints": constraints,
        "outputs_hint": {
            "guidance": True,
            "code": {
                "enabled": False
            }
        },
        "note": "This is a draft scaffold only. Human must author final intent."
    }
