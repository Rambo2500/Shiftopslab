import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List

from intent_to_code.validators.intent_validator import validate_intent
from intent_to_code.executors.router import route_execution
from intent_to_code.support.audit_trace import write_audit_trace
from intent_to_code.support.planner import PlanningKernel
from intent_to_code.system_orchestrator import list_available_templates

def print_header(title: str):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def print_kv(key: str, value: Any):
    print(f"{key:<18}: {value}")

def handle_list_systems(args):
    templates = list_available_templates()
    print_header("AVAILABLE SYSTEM TEMPLATES")
    for t in templates:
        print(f"- {t['id']:<30} [{t['components']} components]")
        print(f"  {t['description']}")

def handle_run(args):
    intent_path = Path(args.intent)
    if not intent_path.exists():
        print(f"Error: Intent file not found: {args.intent}")
        sys.exit(1)
        
    with open(intent_path, "r", encoding="utf-8") as f:
        intent = json.load(f)

    # Inject flags
    if args.bootstrap:
        if "outputs" not in intent: intent["outputs"] = {}
        if "code" not in intent["outputs"]: intent["outputs"]["code"] = {}
        intent["outputs"]["code"]["bootstrap_env"] = True
        if "system" in intent["outputs"]:
            intent["outputs"]["system"]["bootstrap_env"] = True

    validation = validate_intent(intent)
    if not validation["valid"]:
        print_header("VALIDATION FAILED")
        for e in validation["errors"]:
            print(f"- {e['path']} [{e['code']}]: {e['message']}")
        sys.exit(1)

    validated_intent = validation["validated_intent"]
    execute_intent(validated_intent, dry_run=args.dry_run)

def handle_build(args):
    """
    The "Universal System Compiler" entry point.
    Draft -> Validate -> Execute
    """
    print_header("PLANNING SYSTEM")
    planner = PlanningKernel()
    validated_intent = planner.plan_system(args.request)
    
    if "error" in validated_intent:
        print(f"Planning failed: {validated_intent['error']}")
        if "errors" in validated_intent:
            for e in validated_intent["errors"]:
                print(f"- {e['path']} [{e['code']}]: {e['message']}")
        sys.exit(1)

    print_kv("Goal", validated_intent["goal"])
    print_kv("Mode", "Dry-run" if args.dry_run else "Live")
    
    execute_intent(validated_intent, dry_run=args.dry_run)

def execute_intent(intent: Dict[str, Any], dry_run: bool):
    print_header("EXECUTING BUILD")
    
    # Check for System / Component Graph
    system_request = intent.get("outputs", {}).get("system", {})
    if system_request.get("enabled"):
        components = system_request.get("components", [])
        if components:
            print("Component Graph (Topologically Sorted):")
            for c in components:
                deps = c.get("depends_on", [])
                dep_str = f" -> [{', '.join(deps)}]" if deps else " (root)"
                print(f"  - {c['name']:<20} [{c['type']}] {dep_str}")
            print("-" * 60)

    results = route_execution(intent, preview=dry_run)
    
    write_audit_trace({
        "stage": "cli_execution",
        "mode": "dry-run" if dry_run else "live",
        "intent_goal": intent.get("goal"),
        "results": results
    })

    if not results:
        print("(no actions performed)")
        return

    for idx, r in enumerate(results, start=1):
        print(f"\nStep {idx}: {r.get('type')}")
        if "result" in r:
            res = r["result"]
            if "system" in res:
                print(f"  Orchestrated System: {res['system']}")
                print(f"  Components Compiled: {res['components_compiled']}")
            elif "artifact" in res:
                art = res["artifact"]
                print(f"  Compiled Artifact: {art['type']}")
                print(f"  Path: {art['path']}")
        elif "action" in r:
            print(f"  Planned Action: {r['action']}")

    print_header("BUILD COMPLETE")

def main():
    parser = argparse.ArgumentParser(description="Intent-to-Code: Software Architecture Compiler")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Command: build
    build_parser = subparsers.add_parser("build", help="Build a system from a natural language request")
    build_parser.add_argument("request", help="Natural language request (e.g. 'warehouse analytics dashboard')")
    build_parser.add_argument("--dry-run", action="store_true", help="Preview the plan without executing")

    # Command: run
    run_parser = subparsers.add_parser("run", help="Run an existing intent JSON file")
    run_parser.add_argument("intent", help="Path to the intent JSON file")
    run_parser.add_argument("--dry-run", action="store_true", help="Preview the execution without running")
    run_parser.add_argument("--bootstrap", action="store_true", help="Force bootstrap_env for generated code")

    # Command: list-systems
    subparsers.add_parser("list-systems", help="List available system templates")

    args = parser.parse_args()

    if args.command == "build":
        handle_build(args)
    elif args.command == "run":
        handle_run(args)
    elif args.command == "list-systems":
        handle_list_systems(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
