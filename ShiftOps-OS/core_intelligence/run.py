import sys
import json
from pathlib import Path
from typing import Dict, Any

from intent_to_code.validators.intent_validator import validate_intent
from intent_to_code.executors.router import route_execution
from intent_to_code.support.audit_trace import write_audit_trace


def load_stub_intent(text: str) -> Dict[str, Any]:
    return {
        "validated": False,
        "NON_EXECUTABLE_PLAN": True,
        "goal": text,
        "outputs": {},
        "security_envelope": {}
    }


def load_intent_from_file(path_str: str) -> Dict[str, Any]:
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"Intent file not found: {path_str}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python run.py \"<human request>\"")
        print("  python run.py --intent <intent.json>")
        sys.exit(1)

    args = sys.argv[1:]

    # ---- Load intent ----
    if len(args) >= 2 and args[0] == "--intent":
        intent = load_intent_from_file(args[1])
    else:
        text = " ".join(args)
        intent = load_stub_intent(text)

    # ---- Batch 14: Validation Gate ----
    validation = validate_intent(intent)

    if not validation["valid"]:
        write_audit_trace({
            "stage": "validation",
            "status": "failed",
            "errors": validation["errors"]
        })
        print("Execution halted by validator.")
        sys.exit(1)

    validated_intent = validation["validated_intent"]

    # ---- Router execution ----
    results = route_execution(validated_intent)

    # ---- Batch 16: Audit Trace ----
    write_audit_trace({
        "stage": "execution",
        "status": "completed",
        "outputs": results
    })

    # ---- Output to console ----
    if not results:
        print("(no execution outputs)")
    else:
        print(json.dumps(results, indent=2))

