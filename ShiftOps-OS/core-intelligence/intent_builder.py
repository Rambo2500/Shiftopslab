import sys
import json
from intent_to_code.support.planner import PlanningKernel
from intent_to_code.executors.router import route_execution
from intent_to_code.support.audit_trace import write_audit_trace

def build_from_request(user_request: str, dry_run: bool = False):
    """
    The unified one-shot builder experience.
    1. Plan
    2. Validate (done inside Planner)
    3. Route / Build
    """
    # 1. Plan (Architectural Layer)
    planner = PlanningKernel()
    validated_intent = planner.plan_system(user_request)
    
    if "error" in validated_intent:
        print(f"Planning failed: {validated_intent['error']}")
        return

    # 2. Execute / Compile (Deterministic Layer)
    print("\nExecuting build...")
    results = route_execution(validated_intent, preview=dry_run)
    
    # 3. Audit / Record
    write_audit_trace({
        "stage": "one-shot-build",
        "user_request": user_request,
        "mode": "dry-run" if dry_run else "live",
        "intent_goal": validated_intent["goal"],
        "results": results
    })
    
    print("\nBuild Complete.")
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python intent_builder.py \"<user request>\"")
        sys.exit(1)
        
    request = sys.argv[1]
    build_from_request(request)
