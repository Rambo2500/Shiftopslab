"""
Guidance Executor

Renders guidance into a deterministic checklist.
Supports both legacy {goal, steps[]} and current {sections:[{title, bullets[]}]} payloads.
No inference. No execution.
"""

from typing import Dict, List, Any


def execute_guidance(guidance: Dict[str, Any]) -> List[str]:
    lines: List[str] = []

    # --- Legacy format ---
    if isinstance(guidance.get("steps"), list):
        goal = guidance.get("goal", "Untitled Guidance")
        steps = guidance.get("steps", [])

        lines.append(f"# Guidance: {goal}")
        lines.append("")

        for step in sorted(steps, key=lambda s: s.get("order", 0)):
            order = step.get("order", "?")
            desc = (step.get("description", "") or "").strip()
            if desc:
                lines.append(f"- [{order}] {desc}")
        return lines

    # --- Current format (Batch 11) ---
    sections = guidance.get("sections")
    title = "Guidance"

    lines.append(f"# Guidance: {title}")
    lines.append("")

    if isinstance(sections, list):
        for sec in sections:
            sec_title = sec.get("title") if isinstance(sec, dict) else None
            bullets = sec.get("bullets") if isinstance(sec, dict) else None

            if sec_title and isinstance(sec_title, str):
                lines.append(f"## {sec_title}")
                lines.append("")

            if isinstance(bullets, list):
                for i, b in enumerate(bullets, start=1):
                    if isinstance(b, str) and b.strip():
                        lines.append(f"- [{i}] {b.strip()}")
                lines.append("")

    return lines
