from typing import Dict, Any, List


class LintResult:
    def __init__(self, warnings: List[str]):
        self.warnings = warnings

    def to_dict(self) -> Dict[str, Any]:
        return {
            "warnings": self.warnings
        }


def lint_intent(intent: Dict[str, Any]) -> LintResult:
    """
    Non-authoritative intent linter.

    Produces human-facing warnings only.
    Does not block execution.
    Does not modify intent.
    Does not infer behavior.
    """

    warnings: List[str] = []

    # 1. Missing or empty constraints
    constraints = intent.get("constraints")
    if not constraints:
        warnings.append(
            "No constraints specified — intent grants maximum freedom to the compiler."
        )

    # 2. Context references without usage notes
    for ref in intent.get("context_references", []):
        if "usage_note" not in ref or not ref["usage_note"].strip():
            warnings.append(
                f"Context reference '{ref.get('context_id')}' has no usage_note explaining how it informed intent."
            )

    # 3. Context referenced but not otherwise mentioned
    if intent.get("context_references"):
        goal_text = intent.get("goal", "").lower()
        mentioned = any(
            ref.get("context_id", "").lower() in goal_text
            for ref in intent["context_references"]
        )
        if not mentioned:
            warnings.append(
                "Context referenced but not mentioned in goal or constraints — ensure relevance is clear."
            )

    return LintResult(warnings=warnings)
