# batches/batch_22_passive_harvester.py
"""
Batch 22 - OpenAI Reasoning Enrichment Provider (deterministic, structured)

What it is:
- Calls OpenAI for structured reasoning enrichment.
- Preserves deterministic compiler spine.
- Returns same context shape expected by Batch 11.

Design:
- AI is advisory only.
- Never authoritative.
- Never modifies execution.
- Always schema-tolerant.
"""

from __future__ import annotations

import os
from typing import Any, Dict

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # graceful fallback


MODEL_NAME = "gpt-4.1-mini"
MAX_TOKENS = 800


def run_batch_22_passive_harvester(context: Dict[str, Any]) -> Dict[str, Any]:
    intent = context.get("intent") or {}

    # Only run when guidance requested
    outputs = intent.get("outputs") or {}
    if not isinstance(outputs, dict) or not outputs.get("guidance", False):
        return context

    # Respect security envelope outbound policy
    env = intent.get("security_envelope") or {}
    outbound_policy = (env.get("network") or {}).get("outbound")
    if outbound_policy and str(outbound_policy).upper() == "DENY_ALL":
        context["harvest"] = {
            "provider": "none",
            "text": "",
            "warnings": ["outbound_denied_skip_enrichment"],
        }
        context["passive_ai"] = ""
        return context

    # Check API availability
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        context["harvest"] = {
            "provider": "none",
            "text": "",
            "warnings": ["openai_not_configured"],
        }
        context["passive_ai"] = ""
        return context

    query = _build_query(intent)

    try:
        client = OpenAI()

        response = client.responses.create(
            model=MODEL_NAME,
            max_output_tokens=MAX_TOKENS,
            input=_build_prompt(query)
        )

        reasoning_text = _extract_text(response)

        context["harvest"] = {
            "provider": "openai_reasoning",
            "text": reasoning_text,
            "warnings": [],
            "query": query,
        }

        context["passive_ai"] = reasoning_text

    except Exception as e:
        context["harvest"] = {
            "provider": "openai_reasoning",
            "text": "",
            "warnings": [f"openai_error:{str(e)}"],
            "query": query,
        }
        context["passive_ai"] = ""

    return context


# ---- Internal helpers ----

def _build_query(intent: Dict[str, Any]) -> str:
    g = intent.get("guidance") or {}
    if isinstance(g, dict):
        topic = g.get("topic")
        if isinstance(topic, str) and topic.strip():
            return topic.strip()

        ggoal = g.get("goal")
        if isinstance(ggoal, str) and ggoal.strip():
            return ggoal.strip()

    goal = intent.get("goal")
    if isinstance(goal, str) and goal.strip():
        return goal.strip()

    return "small automation project plan"


def _build_prompt(query: str) -> str:
    return f"""
You are producing structured operational guidance.

Respond with 5 to 10 short declarative sentences.
No bullet points.
No numbering.
No headings.
No markdown.
No formatting.
No section labels.

Request:
{query}

Provide clear, direct, actionable sentences only.
"""


def _extract_text(response) -> str:
    try:
        if hasattr(response, "output_text") and response.output_text:
            return response.output_text.strip()

        if hasattr(response, "output"):
            parts = []
            for item in response.output:
                if hasattr(item, "content"):
                    for c in item.content:
                        if hasattr(c, "text"):
                            parts.append(c.text)
            return "\n".join(parts).strip()

    except Exception:
        pass

    return ""
