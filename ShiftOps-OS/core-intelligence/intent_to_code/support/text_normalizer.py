# support/text_normalizer.py
"""
Batch 21 - Guidance quality controls

What it is:
- Deterministic normalizer that turns HTML/markdown-ish blobs into clean text + bullets.

What it's for:
- Make passive AI harvest output readable and usable as guidance markdown.
- Provide a deterministic quality_score so downstream can flag low-signal output.

Where it fails:
- If input is empty, boilerplate-heavy, or fully blocked by network/engine,
  it will return low score + warnings (but still deterministic).

Constraints:
- Standard library only (no bs4, no lxml).
- No network, no SDKs, no external calls.
"""

from __future__ import annotations

import html as _html
import re
import unicodedata
from typing import Dict, List, Tuple


# A conservative set of boilerplate patterns commonly seen in search/engine pages.
_BOILERPLATE_PATTERNS = [
    r"\baccept (all )?cookies\b",
    r"\bcookie(s)?\b",
    r"\bprivacy\b",
    r"\bterms\b",
    r"\bsign in\b",
    r"\blog in\b",
    r"\benable javascript\b",
    r"\bturn on javascript\b",
    r"\buse of this site\b",
    r"\ball rights reserved\b",
    r"\bsubscribe\b",
    r"\bnewsletter\b",
    r"\badvertis(e|ing)\b",
    r"\bskip to content\b",
    r"\baccessibility\b",
    r"\bconsent\b",
    r"\bpreferences\b",
]


def normalize_guidance_blob(raw: str, *, max_bullets: int = 14) -> Dict[str, object]:
    """
    Normalize a harvested blob (often HTML) into deterministic guidance artifacts.

    Returns dict:
      {
        "text": <cleaned_text>,
        "bullets": [..],
        "quality_score": <float 0..1>,
        "warnings": [..],
        "stats": {...}
      }
    """
    warnings: List[str] = []
    if raw is None:
        raw = ""
    if not isinstance(raw, str):
        raw = str(raw)

    original_len = len(raw)

    # 1) Normalize unicode + newlines early
    s = unicodedata.normalize("NFKC", raw).replace("\r\n", "\n").replace("\r", "\n")

    # 2) If it smells like HTML, strip tags.
    #    (We do this always; even if not HTML, it is safe.)
    s = _strip_html(s)

    # 3) Decode HTML entities
    s = _html.unescape(s)

    # 4) Remove obvious boilerplate lines
    lines = [ln.strip() for ln in s.split("\n")]
    lines = [ln for ln in lines if ln]
    kept_lines, removed_count = _filter_boilerplate_lines(lines)

    if not kept_lines:
        warnings.append("NORMALIZER_EMPTY_AFTER_FILTER")
        cleaned_text = ""
        bullets: List[str] = []
        quality = 0.0
        return {
            "text": cleaned_text,
            "bullets": bullets,
            "quality_score": quality,
            "warnings": warnings,
            "stats": {
                "original_len": original_len,
                "removed_lines": removed_count,
                "kept_lines": 0,
            },
        }

    # 5) Collapse into paragraphs
    cleaned_text = _collapse_whitespace("\n".join(kept_lines))

    # 6) Generate bullets (deterministic)
    bullets = _make_bullets(cleaned_text, max_bullets=max_bullets)

    # 7) Score quality
    quality, score_warnings = _quality_score(cleaned_text, bullets)
    warnings.extend(score_warnings)

    return {
        "text": cleaned_text,
        "bullets": bullets,
        "quality_score": quality,
        "warnings": warnings,
        "stats": {
            "original_len": original_len,
            "removed_lines": removed_count,
            "kept_lines": len(kept_lines),
        },
    }


def _strip_html(s: str) -> str:
    # Remove script/style blocks first
    s = re.sub(r"(?is)<script.*?>.*?</script>", "\n", s)
    s = re.sub(r"(?is)<style.*?>.*?</style>", "\n", s)

    # Replace <br> and block tags with newlines
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?i)</(p|div|li|ul|ol|h1|h2|h3|h4|h5|h6|section|article|header|footer|nav)>", "\n", s)

    # Strip all remaining tags
    s = re.sub(r"(?s)<[^>]+>", " ", s)

    # De-junk common HTML leftovers
    s = s.replace("\u00a0", " ")  # nbsp
    return s


def _filter_boilerplate_lines(lines: List[str]) -> Tuple[List[str], int]:
    removed = 0
    kept: List[str] = []
    compiled = [re.compile(pat, flags=re.IGNORECASE) for pat in _BOILERPLATE_PATTERNS]

    for ln in lines:
        # Skip very short nav-like fragments
        if len(ln) <= 2:
            removed += 1
            continue

        # Skip lines that are mostly punctuation/symbols
        if _punct_ratio(ln) > 0.55:
            removed += 1
            continue

        # Skip boilerplate patterns
        if any(rx.search(ln) for rx in compiled):
            removed += 1
            continue

        # Skip repeated cookie-banner-ish phrases (extra guard)
        low = ln.lower()
        if "cookie" in low and ("accept" in low or "consent" in low):
            removed += 1
            continue

        kept.append(ln)

    return kept, removed


def _collapse_whitespace(s: str) -> str:
    # Normalize whitespace while preserving newlines where useful.
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def _make_bullets(text: str, *, max_bullets: int) -> List[str]:
    """
    Deterministic bulletization:
      - Split by sentence-ish boundaries and line breaks
      - Keep medium/long units
      - Deduplicate (case-insensitive)
    """
    # Split on blank lines first, then sentence boundaries
    chunks: List[str] = []
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if not para:
            continue
        # Sentence split (conservative)
        parts = re.split(r"(?<=[\.\!\?])\s+", para)
        for p in parts:
            p = p.strip()
            if p:
                chunks.append(p)

    # Clean and filter
    out: List[str] = []
    seen = set()
    for c in chunks:
        c = c.strip(" -•\t")
        c = re.sub(r"\s+", " ", c).strip()

        # Drop extremely short fragments
        if len(c) < 20:
            continue

        key = c.lower()
        if key in seen:
            continue
        seen.add(key)

        # Trim to reasonable bullet length
        if len(c) > 220:
            c = c[:217].rstrip() + "…"

        out.append(c)
        if len(out) >= max_bullets:
            break

    return out


def _quality_score(text: str, bullets: List[str]) -> Tuple[float, List[str]]:
    """
    Deterministic heuristic scoring in [0,1].
    Emphasis:
      - Having bullets
      - Reasonable text length
      - Low boilerplate smell
      - Low repetition
    """
    warnings: List[str] = []
    if not text and not bullets:
        return 0.0, ["QUALITY_EMPTY"]

    score = 0.0

    # Signal 1: bullets exist
    if bullets:
        score += 0.35
    else:
        warnings.append("QUALITY_NO_BULLETS")

    # Signal 2: text length
    n = len(text)
    if n >= 400:
        score += 0.25
    elif n >= 200:
        score += 0.18
    elif n >= 80:
        score += 0.10
    else:
        warnings.append("QUALITY_SHORT_TEXT")

    # Signal 3: bullet count
    bc = len(bullets)
    if bc >= 8:
        score += 0.20
    elif bc >= 4:
        score += 0.14
    elif bc >= 1:
        score += 0.07
    else:
        # already warned above
        pass

    # Signal 4: repetition penalty
    rep = _repetition_ratio(bullets)
    if rep < 0.15:
        score += 0.10
    elif rep < 0.30:
        score += 0.05
    else:
        warnings.append("QUALITY_REPETITIVE_BULLETS")

    # Signal 5: boilerplate smell
    smell = _boilerplate_smell(text)
    if smell < 0.10:
        score += 0.10
    elif smell < 0.25:
        score += 0.05
    else:
        warnings.append("QUALITY_BOILERPLATE_SMELL")

    # Clamp
    if score < 0.0:
        score = 0.0
    if score > 1.0:
        score = 1.0

    # Final sanity warnings
    if score < 0.25:
        warnings.append("QUALITY_LOW")

    return score, warnings


def _repetition_ratio(bullets: List[str]) -> float:
    if not bullets:
        return 1.0
    # Compare normalized first 10 words per bullet
    sigs = []
    for b in bullets:
        words = re.findall(r"[a-zA-Z0-9]+", b.lower())[:10]
        sigs.append(" ".join(words))
    unique = len(set(sigs))
    return 1.0 - (unique / max(1, len(sigs)))


def _boilerplate_smell(text: str) -> float:
    """
    Fraction of tokens that match boilerplate-ish keywords.
    This is intentionally rough and deterministic.
    """
    if not text:
        return 1.0
    tokens = re.findall(r"[a-zA-Z]{3,}", text.lower())
    if not tokens:
        return 1.0

    keywords = {
        "cookie", "privacy", "terms", "subscribe", "consent", "preferences",
        "advertising", "newsletter", "login", "signin", "javascript",
        "accessibility"
    }
    hits = sum(1 for t in tokens if t in keywords)
    return hits / max(1, len(tokens))


def _punct_ratio(s: str) -> float:
    if not s:
        return 1.0
    punct = sum(1 for ch in s if not ch.isalnum() and not ch.isspace())
    return punct / max(1, len(s))
