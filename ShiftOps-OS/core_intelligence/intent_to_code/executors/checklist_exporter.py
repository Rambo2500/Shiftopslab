"""
Checklist exporter execution path (optional).

Converts guidance into a human-readable checklist.
No code generation. No mutation. Deterministic output.
"""

from typing import Dict, List


def export_checklist(guidance: Dict) -> Dict:
    """
    Export guidance steps as a Markdown checklist.

    Assumes guidance has already been validated.
    """
    goal = guidance.get("goal", "")
    steps: List[Dict] = guidance.get("steps", [])

    lines = [
        f"# Checklist: {goal}",
        ""
    ]

    for step in sorted(steps, key=lambda s: s.get("order", 0)):
        desc = step.get("description", "")
        lines.append(f"- [ ] {desc}")

    markdown = "\n".join(lines)

    return {
        "format": "markdown",
        "content": markdown
    }
