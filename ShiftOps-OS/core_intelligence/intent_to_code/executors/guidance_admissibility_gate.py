"""
Guidance Admissibility Gate (deterministic)

Hard-rejects non-guidance bullets (marketing/CTA/SEO fragments).
Relaxes generic rule for trusted model providers.

Input: guidance_payload (dict)
Output: (filtered_payload, rejection_report)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import re


@dataclass(frozen=True)
class Rejection:
    bullet: str
    reason_code: str


CTA_VERBS = {
    "browse", "discover", "find", "shop", "buy", "sign up", "signup", "start free",
    "get started", "learn more", "request a demo", "try", "download"
}

PROMO_PHRASES = {
    "best", "top", "leading", "award-winning", "trusted", "confidently",
    "verified user reviews", "compare products", "compare the best"
}

BRAND_BLACKLIST = {
    "capterra", "g2", "gartner", "forrester", "trustpilot"
}

INSTRUCTION_VERBS = {
    "select", "choose", "identify", "define", "plan", "evaluate", "consider",
    "document", "measure", "test", "implement", "review", "validate",
    "configure", "build", "create", "establish", "ensure", "start", "scope",
    "deploy", "monitor", "adjust"
}


def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def _contains_any(haystack: str, needles: set[str]) -> bool:
    return any(n in haystack for n in needles)


def _is_marketing_or_cta(text_norm: str) -> Tuple[bool, str]:
    for b in BRAND_BLACKLIST:
        if b in text_norm:
            return True, "BRAND_MENTION"

    for cta in CTA_VERBS:
        if cta in text_norm:
            return True, "CTA_LANGUAGE"

    for promo in PROMO_PHRASES:
        if promo in text_norm:
            return True, "PROMOTIONAL_LANGUAGE"

    return False, ""


def _is_instructional(text_norm: str) -> bool:
    return _contains_any(text_norm, INSTRUCTION_VERBS)


def apply_guidance_admissibility_gate(
    guidance_payload: Dict[str, Any]
) -> Tuple[Dict[str, Any], Dict[str, Any]]:

    payload = guidance_payload or {}
    sections = payload.get("sections", [])
    provider = payload.get("provider")

    rejections: List[Rejection] = []
    kept_count = 0
    dropped_count = 0
    filtered_sections: List[Dict[str, Any]] = []

    for sec in sections:
        bullets = sec.get("bullets", [])
        filtered_bullets: List[str] = []

        for bullet in bullets:
            if not isinstance(bullet, str):
                dropped_count += 1
                rejections.append(Rejection(str(bullet), "NON_STRING"))
                continue

            b_norm = _normalize(bullet)

            if len(b_norm) < 20:
                dropped_count += 1
                rejections.append(Rejection(bullet, "TOO_SHORT"))
                continue

            is_bad, bad_code = _is_marketing_or_cta(b_norm)
            if is_bad:
                dropped_count += 1
                rejections.append(Rejection(bullet, bad_code))
                continue

            if not _is_instructional(b_norm):
                dropped_count += 1
                rejections.append(Rejection(bullet, "NOT_INSTRUCTIONAL"))
                continue

            # 👇 Relax generic rule for trusted model provider
            if provider != "openai_reasoning":
                # Original anti-generic rule preserved for search engines
                if len(b_norm.split()) < 6:
                    dropped_count += 1
                    rejections.append(Rejection(bullet, "GENERIC_STATEMENT"))
                    continue

            filtered_bullets.append(bullet.strip())
            kept_count += 1

        filtered_sec = dict(sec)
        filtered_sec["bullets"] = filtered_bullets
        filtered_sections.append(filtered_sec)

    filtered_payload = dict(payload)
    filtered_payload["sections"] = filtered_sections
    filtered_payload["admissibility"] = {
        "kept": kept_count,
        "dropped": dropped_count
    }

    rejection_report = {
        "kept": kept_count,
        "dropped": dropped_count,
        "rejections": [
            {"bullet": r.bullet, "reason_code": r.reason_code} for r in rejections
        ]
    }

    return filtered_payload, rejection_report
