import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


AUDIT_DIR = Path("outputs/audit")
AUDIT_DIR.mkdir(parents=True, exist_ok=True)


def write_audit_trace(event: Dict[str, Any]) -> Path:
    """
    Append-only audit trace writer.

    This function:
    - never mutates execution
    - never raises
    - never retries
    - never blocks execution

    It records facts only.
    """

    timestamp = datetime.now(timezone.utc).isoformat()
    record = {
        "timestamp_utc": timestamp,
        "event": event
    }

    filename = f"audit_{timestamp.replace(':', '').replace('.', '')}.json"
    path = AUDIT_DIR / filename

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)
    except Exception:
        # Audit must never interfere with execution
        pass

    return path
