from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class GuidanceUnit:
    """
    Lossless composite unit of directional guidance.

    A GuidanceUnit preserves the smallest chunk of source content
    that still carries actionable direction, without inference,
    rewriting, or judgment.

    This is the canonical unit evaluated by governance.
    """

    # Stable identifier for audit + trace
    id: str

    # Source metadata (kept minimal, additive)
    source: Dict[str, Any]
    # Example:
    # {
    #   "engine": "bing" | "passive",
    #   "url": "https://...",
    #   "section_index": 0,
    #   "paragraph_index": 3
    # }

    # Full composite text (sentences preserved in original order)
    text: str

    # Individual sentences that compose the unit
    sentences: List[str]

    # Convenience field for downstream logic / audits
    sentence_count: int
