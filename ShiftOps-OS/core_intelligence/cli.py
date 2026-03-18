import sys
import json
from pathlib import Path

from intent_to_code.validators.intent_validator import validate_intent
from intent_to_code.executors.router import route_execution
from intent_to_code.support.audit_trace import write_audit_trace


def load_intent_from_file(path_str: str):
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"Intent file not found: {path_str}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def print_header(title: str):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def print_kv(key: str, value: str):
    print(f"{key:<18}: {value}")


def main():
    args = sys.argv[1:]

    if not args or "--help" in args:
        print("Usage:")
        print("  python cli.py --intent intent.json [--dry-run] [--explain] [--raw] [--bootstrap] [--system <type>]")
        sys.exit(0)

    dry_run = "--dry-run" in args
    explain = "--explain" in args
    raw = "--raw" in args
    bootstrap = "--bootstrap" in args
    list_systems = "--list-systems" in args
    platform = "--platform" in args
    
    if list_systems:
        from intent_to_code.system_orchestrator import list_available_templates
        templates = list_available_templates()
        print_header("AVAILABLE SYSTEM TEMPLATES")
        for t in templates:
            print(f"- {t['id']:<30} [{t['components']} components]")
            print(f"  {t['description']}")
        sys.exit(0)

    system_type = None
    if "--system" in args:
        system_type = args[args.index("--system") + 1]

    if "--intent" not in args:
        print("Error: --intent <file> is required")
        sys.exit(1)

    intent_path = args[args.index("--intent") + 1]
    intent = load_intent_from_file(intent_path)

    # ---- Phase 3/4/6: Inject flags into intent ----
    if bootstrap or system_type or platform:
        if "outputs" not in intent:
            intent["outputs"] = {}
        
        if bootstrap:
            if "code" not in intent["outputs"]:
                intent["outputs"]["code"] = {}
            intent["outputs"]["code"]["bootstrap_env"] = True
            
        if system_type:
            intent["outputs"]["system"] = {
                "enabled": True,
                "type": system_type,
                "bootstrap_env": bootstrap
            }
            
        if platform:
            intent["outputs"]["platform"] = {
                "enabled": True
            }

    # ---- Validation gate ----
    validation = validate_intent(intent)

    if not validation["valid"]:
        print_header("VALIDATION FAILED")
        for e in validation["errors"]:
            print(f"- {e['path']} [{e['code']}]: {e['message']}")

        write_audit_trace({
            "stage": "validation",
            "status": "failed",
            "errors": validation["errors"]
        })
        sys.exit(1)

    validated_intent = validation["validated_intent"]

    # ---- Execute or Replay ----
    results = route_execution(validated_intent, preview=dry_run)

    write_audit_trace({
        "stage": "execution",
        "status": "completed",
        "mode": "dry-run" if dry_run else "live",
        "outputs": results
    })

    # ---- Raw JSON output (opt-in) ----
    if raw:
        print(json.dumps(results, indent=2))
        sys.exit(0)

    # ---- Human-readable output ----
    if dry_run:
        print_header("DRY-RUN — EXECUTION PLAN")
        print_kv("Mode", "Replay / No execution")
    else:
        print_header("EXECUTION COMPLETE")
        print_kv("Mode", "Live execution")

    if not results:
        print("\n(no actions)")
        sys.exit(0)

    for idx, r in enumerate(results, start=1):
        print("\n" + "-" * 60)
        print(f"Step {idx}")
        for k, v in r.items():
            if isinstance(v, (dict, list)):
                print_kv(k, "[complex]")
            else:
                print_kv(k, str(v))

    if explain and dry_run:
        print_header("EXPLANATION")
        for r in results:
            action = r.get("action")
            if action:
                print(f"- {r['type']}: {action}")


if __name__ == "__main__":
    main()
