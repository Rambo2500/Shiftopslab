"""
Batch 22 providers: passive, zero-cost harvesting via curl + HTML snippet extraction.

Observed constraints:
- No SDKs
- No paid APIs
- No agent loops
- Must be deterministic

Outputs:
- provider name
- harvested text (plain)
- warnings list
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Tuple
from urllib.parse import quote_plus


USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

DEFAULT_TIMEOUT_SEC = 15


@dataclass(frozen=True)
class HarvestResult:
    provider: str
    text: str
    warnings: List[str]


def _curl_get(url: str, timeout_sec: int = DEFAULT_TIMEOUT_SEC) -> Tuple[str, List[str]]:
    warnings: List[str] = []
    try:
        proc = subprocess.run(
            ["curl", "-sL", "-A", USER_AGENT, "--max-time", str(timeout_sec), url],
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            warnings.append(f"curl_nonzero_exit:{proc.returncode}")
            if proc.stderr:
                warnings.append("curl_stderr_present")
            return "", warnings
        return proc.stdout or "", warnings
    except FileNotFoundError:
        return "", ["curl_missing"]
    except Exception:
        return "", ["curl_exception"]


_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def _html_to_text_basic(html: str) -> str:
    if not html:
        return ""
    html = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    html = re.sub(r"(?is)<style.*?>.*?</style>", " ", html)
    text = _TAG_RE.sub(" ", html)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'")
    text = _WS_RE.sub(" ", text).strip()
    return text


def _take_top_sentences(text: str, max_chars: int = 2500) -> str:
    if not text:
        return ""
    return text[:max_chars].strip()


def fetch_duckduckgo(query: str) -> HarvestResult:
    q = quote_plus(query)
    url = f"https://duckduckgo.com/html/?q={q}"
    html, warnings = _curl_get(url)
    if not html:
        return HarvestResult("duckduckgo", "", warnings + ["empty_response"])

    snippets = re.findall(
        r'(?is)<a[^>]*class="result__a"[^>]*>.*?</a>.*?<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
        html
    )
    if not snippets:
        snippets = re.findall(r'(?is)class="result__snippet"[^>]*>(.*?)</a>', html)

    if snippets:
        joined = "\n".join(_html_to_text_basic(s) for s in snippets[:8])
        return HarvestResult("duckduckgo", _take_top_sentences(joined), warnings)

    text = _html_to_text_basic(html)
    return HarvestResult("duckduckgo", _take_top_sentences(text), warnings + ["fallback_fullpage"])


def fetch_bing(query: str) -> HarvestResult:
    q = quote_plus(query)
    url = f"https://www.bing.com/search?q={q}"
    html, warnings = _curl_get(url)

    # ===== DEBUG: RAW HTML INSPECTION =====
    print("\n=== BING RAW HTML SAMPLE START ===")
    if html:
        print(html[:20000])
    else:
        print("(no html returned)")
    print("=== BING RAW HTML SAMPLE END ===\n")
    # ======================================

    if not html:
        return HarvestResult("bing", "", warnings + ["empty_response"])

    snippets = re.findall(r'(?is)<li class="b_algo".*?<p>(.*?)</p>', html)
    if snippets:
        joined = "\n".join(_html_to_text_basic(s) for s in snippets[:8])
        return HarvestResult("bing", _take_top_sentences(joined), warnings)

    text = _html_to_text_basic(html)
    return HarvestResult("bing", _take_top_sentences(text), warnings + ["fallback_fullpage"])


def fetch_google(query: str) -> HarvestResult:
    q = quote_plus(query)
    url = f"https://www.google.com/search?q={q}&hl=en"
    html, warnings = _curl_get(url)
    if not html:
        return HarvestResult("google", "", warnings + ["empty_response"])

    snippets = re.findall(r'(?is)<div class="VwiC3b[^"]*">(.*?)</div>', html)
    if snippets:
        joined = "\n".join(_html_to_text_basic(s) for s in snippets[:6])
        return HarvestResult("google", _take_top_sentences(joined), warnings)

    text = _html_to_text_basic(html)
    return HarvestResult("google", _take_top_sentences(text), warnings + ["fallback_fullpage"])


def choose_provider_det(query: str, preferred: Optional[List[str]] = None, min_chars: int = 200) -> HarvestResult:
    order = preferred or ["bing", "duckduckgo", "google"]

    results: List[HarvestResult] = []
    for name in order:
        if name == "bing":
            results.append(fetch_bing(query))
        elif name == "duckduckgo":
            results.append(fetch_duckduckgo(query))
        elif name == "google":
            results.append(fetch_google(query))
        else:
            results.append(HarvestResult(name, "", ["unknown_provider"]))

    for r in results:
        if len(r.text) >= min_chars:
            return r

    for r in results:
        if r.text:
            return HarvestResult(r.provider, r.text, r.warnings + ["below_min_chars"])

    return HarvestResult("none", "", ["no_provider_returned_text"])
