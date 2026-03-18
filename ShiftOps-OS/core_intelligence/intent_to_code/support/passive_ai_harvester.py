import subprocess
from typing import Dict, Any


def harvest_ai_summary(query: str) -> Dict[str, Any]:
    """
    Passive AI reasoning harvest.

    - Zero cost
    - No SDKs
    - No retries
    - No interpretation
    - No authority

    Uses a system browser/search tool to retrieve
    AI-generated summary text already produced by the engine.

    Failure returns empty content.
    """

    if not query:
        return {"query": query, "summary": ""}

    try:
        # NOTE:
        # This assumes a system environment where `curl` is available.
        # We fetch the HTML/text of a search results page and extract visible text.
        # No parsing logic beyond raw capture — normalization happens downstream.

        cmd = [
            "curl",
            "-L",
            "-A",
            "Mozilla/5.0",
            f"https://www.bing.com/search?q={query.replace(' ', '+')}"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        text = result.stdout or ""

    except Exception:
        text = ""

    return {
        "query": query,
        "summary": text.strip()
    }
