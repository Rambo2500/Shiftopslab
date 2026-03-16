import json
from pathlib import Path
from typing import Dict, List

from intent_to_code.compiler import compile_intent

SYSTEM_TEMPLATES_DIR = Path("system_templates")

def list_available_templates() -> List[Dict]:
    """
    Returns a list of available system templates and their metadata.
    """
    templates = []
    if not SYSTEM_TEMPLATES_DIR.exists():
        return []

    for template_file in SYSTEM_TEMPLATES_DIR.glob("*.json"):
        try:
            with open(template_file, "r") as f:
                data = json.load(f)
                templates.append({
                    "id": template_file.stem,
                    "name": data.get("system", template_file.stem),
                    "description": data.get("description", "No description provided."),
                    "components": len(data.get("components", []))
                })
        except Exception:
            pass
    return templates

def orchestrate_system(intent: Dict) -> Dict:
    """
    Orchestrates multi-artifact system generation.
    Supports both pre-defined templates and dynamic component lists.
    """
    system_request = intent.get("outputs", {}).get("system", {})
    if not system_request.get("enabled"):
        return {"error": "System orchestration not enabled in intent"}

    template_name = system_request.get("type")
    
    # Priority: Use dynamic components list if provided (Custom Assembly)
    components = system_request.get("components")
    
    if not components:
        # Fallback: Load from system template file
        template_path = SYSTEM_TEMPLATES_DIR / f"{template_name}.json"
        if not template_path.exists():
            return {"error": f"System template not found: {template_name}"}
        with open(template_path, "r") as f:
            template = json.load(f)
        components = template.get("components", [])
    else:
        # It's a dynamic assembly
        template_name = "dynamic_assembly"

    goal = intent.get("goal") or template_name
    bootstrap_all = system_request.get("bootstrap_env", False)

    results = []
    
    # Base directory for the whole system
    clean_goal = "".join(c if c.isalnum() else "_" for c in goal.lower())
    base_build_dir = Path("build") / clean_goal
    base_build_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nOrchestrating system: {goal}")
    print("Component Graph:")
    for component in components:
        deps = component.get("depends_on", [])
        dep_str = f" -> [{', '.join(deps)}]" if deps else " (root)"
        print(f"  - {component['name']}{dep_str}")
    print("-" * 30)

    # Build a registry of all components to pass as context
    registry = {c["name"]: {"type": c["type"], "depends_on": c.get("depends_on", [])} for c in components}

    for component in components:
        # Create a synthetic intent for the component
        component_intent = {
            "validated": True,
            "NON_EXECUTABLE_PLAN": True,
            "goal": f"{component['name']}",
            "description": component.get("description", ""),
            "inputs": intent.get("inputs", []),
            "outputs": {
                "code": {
                    "enabled": True,
                    "type": component["type"],
                    "bootstrap_env": bootstrap_all
                }
            },
            "system_context": {
                "parent_system": goal,
                "registry": registry, # Full awareness of sibling components
                "name": component["name"],
                "depends_on": component.get("depends_on", [])
            },
            "security_envelope": intent.get("security_envelope", {})
        }
        
        # Compile component into the system's base directory
        compilation_result = compile_intent(component_intent, base_dir=base_build_dir)
        results.append({
            "component": component["name"],
            "result": compilation_result
        })

    return {
        "system": template_name,
        "goal": goal,
        "components_compiled": len(results),
        "artifacts": results
    }
