"""
Batch 11 (updated) - Guidance producer upstream, non-agentic

What it is:
- Produces guidance payload from passive-harvested AI summary output.

What it's for:
- Transform harvested text into:
  1) Lossless composite Guidance Units (for governance)
  2) Normalized bullets (for backward compatibility / diagnostics)

Key correction:
- Preserve composite directional meaning BEFORE bullet normalization.
- Route normalization based on provider source (model vs search).
"""

from __future__ import annotations

from typing import Any, Dict, List
import re
import uuid

from intent_to_code.support.text_normalizer import normalize_guidance_blob
from intent_to_code.support.model_normalizer import normalize_model_guidance
from schemas.guidance_unit import GuidanceUnit


def _split_sentences(text: str) -> List[str]:
    if not text:
        return []

    return [
        s.strip()
        for s in re.split(r"(?<=[.;])\s+", text)
        if s.strip()
    ]


def run(context: Dict[str, Any]) -> Dict[str, Any]:

    intent = context.get("intent") or {}
    outputs_cfg = intent.get("outputs") or {}

    if not outputs_cfg.get("guidance", False):
        return context

    harvested_blob = _extract_harvested_blob(context)

    guidance_units: List[GuidanceUnit] = []

    provider = (context.get("harvest") or {}).get("provider")

    if harvested_blob:
        sentences = _split_sentences(harvested_blob)

        if sentences:
            guidance_units.append(
                GuidanceUnit(
                    id=str(uuid.uuid4()),
                    source={
                        "engine": provider or "unknown",
                        "url": None,
                    },
                    text=" ".join(sentences),
                    sentences=sentences,
                    sentence_count=len(sentences),
                )
            )

    context["guidance_units"] = guidance_units

    # ---- Source-aware normalization ----

    if provider == "openai_reasoning":
        norm = normalize_model_guidance(harvested_blob, max_bullets=14)
    else:
        norm = normalize_guidance_blob(harvested_blob, max_bullets=14)

    guidance_payload = context.get("guidance_payload") or {}

    sections: List[Dict[str, Any]] = [
        {
            "title": "Guidance",
            "bullets": norm.get("bullets", []),
            "quality_score": norm.get("quality_score"),
            "warnings": norm.get("warnings", []),
            "stats": norm.get("stats", {}),
        }
    ]

    guidance_payload.update(
        {
            "sections": sections,
            "raw_excerpt": _safe_excerpt(norm.get("text", ""), 1200),
            "quality_score": norm.get("quality_score"),
            "warnings": norm.get("warnings", []),
            "provider": provider,   # 👈 IMPORTANT
        }
    )

    context["guidance_payload"] = guidance_payload

    return context


def _extract_harvested_blob(context: Dict[str, Any]) -> str:
    for key in ("passive_ai", "harvest", "passive_harvest", "harvester_output"):
        if key not in context:
            continue

        blob = _coerce_blob(context.get(key))
        if blob:
            return blob

    return ""


def _coerce_blob(val: Any) -> str:
    if val is None:
        return ""

    if isinstance(val, str):
        return val

    if isinstance(val, dict):
        for k in ("raw", "content", "summary", "text", "html"):
            if k in val and isinstance(val[k], str):
                return val[k]
        return str(val)

    return str(val)


def _safe_excerpt(text: str, limit: int) -> str:
    if not text:
        return ""

    t = " ".join(text.split())

    if len(t) <= limit:
        return t

    return t[: max(0, limit - 1)].rstrip() + "…"


run_batch_11_guidance_producer = run
