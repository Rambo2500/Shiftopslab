# support/model_normalizer.py
"""
Model-aware guidance normalization.

Used when enrichment provider is OpenAI reasoning.

Design:
- Preserves structured sections (SUMMARY, CONSTRAINTS, RISKS, etc.)
- Avoids HTML/boilerplate stripping logic
- Deterministic
- Standard library only
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple


def normalize_model_guidance(raw: str, *, max_bullets: int = 14) -> Dict[str, object]:
    """
    Normalize model-generated structured reasoning.

    Returns:
      {
        "text": <cleaned_text>,
        "bullets": [..],
        "quality_score": float,
        "warnings": [..],
        "stats": {...}
      }
    """

    warnings: List[str] = []

    if not raw:
        return _empty_result("MODEL_EMPTY")

    # Normalize whitespace
    text = re.sub(r"\r\n", "\n", raw)
    text = re.sub(r"\s+", " ", text).strip()

    # Split into structured sentences
    sentences = _split_sentences(text)

    bullets = []
    for s in sentences:
        s = s.strip()
        if len(s) < 20:
            continue
        if len(s) > 220:
            s = s[:217].rstrip() + "…"
        bullets.append(s)
        if len(bullets) >= max_bullets:
            break

    quality, score_warnings = _quality_score(text, bullets)
    warnings.extend(score_warnings)

    return {
        "text": text,
        "bullets": bullets,
        "quality_score": quality,
        "warnings": warnings,
        "stats": {
            "original_len": len(raw),
            "sentence_count": len(sentences),
            "bullet_count": len(bullets),
        },
    }


def _split_sentences(text: str) -> List[str]:
    return [
        s.strip()
        for s in re.split(r"(?<=[\.\!\?])\s+", text)
        if s.strip()
    ]


def _quality_score(text: str, bullets: List[str]) -> Tuple[float, List[str]]:
    warnings: List[str] = []
    score = 0.0

    if bullets:
        score += 0.4
    else:
        warnings.append("MODEL_NO_BULLETS")

    if len(text) >= 200:
        score += 0.3
    elif len(text) >= 80:
        score += 0.2
    else:
        warnings.append("MODEL_SHORT_TEXT")

    if len(bullets) >= 5:
        score += 0.2
    elif len(bullets) >= 2:
        score += 0.1

    # Mild repetition detection
    unique = len(set(b.lower() for b in bullets))
    if bullets and unique / len(bullets) < 0.7:
        warnings.append("MODEL_REPETITIVE")
    else:
        score += 0.1

    return min(score, 1.0), warnings


def _empty_result(code: str) -> Dict[str, object]:
    return {
        "text": "",
        "bullets": [],
        "quality_score": 0.0,
        "warnings": [code],
        "stats": {
            "original_len": 0,
            "sentence_count": 0,
            "bullet_count": 0,
        },
    }
