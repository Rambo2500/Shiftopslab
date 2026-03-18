"""
Guidance Exporter (Markdown)

Exports rendered guidance lines to a Markdown file.
Deterministic. No mutation. No inference.
"""

from pathlib import Path
from typing import List


def export_guidance_markdown(
    rendered_lines: List[str],
    filename: str
) -> str:
    """
    Write rendered guidance to a markdown file.

    Returns the file path as a string.
    """
    output_dir = Path("outputs/guidance")
    output_dir.mkdir(parents=True, exist_ok=True)

    path = output_dir / filename

    with open(path, "w", encoding="utf-8") as f:
        for line in rendered_lines:
            f.write(line + "\n")

    return str(path)
