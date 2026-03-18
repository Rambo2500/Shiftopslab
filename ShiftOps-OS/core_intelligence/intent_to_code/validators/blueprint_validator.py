import json
from jsonschema import validate, ValidationError
from pathlib import Path
from typing import Dict, Any

class BlueprintValidator:
    def __init__(self, schema_path: str = None):
        # Always find the schema relative to this file's directory
        if schema_path is None:
            # We are in intent_to_code/validators/
            # Go up one level to intent_to_code/, then to contracts/
            base_dir = Path(__file__).parent.parent.parent
            self.schema_path = base_dir / "contracts" / "architecture_blueprint.schema.json"
        else:
            self.schema_path = Path(schema_path)

        if not self.schema_path.exists():
            # Fallback for complex merged repo structures
            root_fallback = Path(__file__).parent.parent.parent.parent / "contracts" / "architecture_blueprint.schema.json"
            if root_fallback.exists():
                self.schema_path = root_fallback
            else:
                raise FileNotFoundError(f"Blueprint schema not found at {self.schema_path} or {root_fallback}")

        print(f"[BlueprintValidator] Loading schema from: {self.schema_path.absolute()}")
        with open(self.schema_path, "r") as f:
            content = f.read()
            print(f"[BlueprintValidator] Content length: {len(content)}")
            if not content.strip():
                print("[BlueprintValidator] ERROR: Schema file is empty!")
            self.schema = json.loads(content)

    def validate_all(self, blueprint: Dict[str, Any]):
        """Runs all validation checks."""
        self.validate_schema(blueprint)
        self.validate_dag(blueprint)
        self.validate_dependencies(blueprint)

    def validate_schema(self, blueprint: Dict[str, Any]):
        """Validates the blueprint against the JSON schema."""
        try:
            validate(instance=blueprint, schema=self.schema)
        except ValidationError as e:
            raise Exception(f"Schema validation failed: {e.message}")

    def validate_dag(self, blueprint: Dict[str, Any]):
        """Ensures the architecture graph is a Directed Acyclic Graph (no cycles)."""
        nodes = blueprint.get("graph", {}).get("nodes", [])
        edges = blueprint.get("graph", {}).get("edges", [])
        
        adj = {node["id"]: [] for node in nodes}
        for edge in edges:
            adj[edge["from"]].append(edge["to"])
            
        visited = set()
        stack = set()
        
        def has_cycle(u):
            visited.add(u)
            stack.add(u)
            for v in adj.get(u, []):
                if v not in visited:
                    if has_cycle(v):
                        return True
                elif v in stack:
                    return True
            stack.remove(u)
            return False
            
        for node in nodes:
            if node["id"] not in visited:
                if has_cycle(node["id"]):
                    raise Exception(f"Dependency cycle detected in blueprint graph at node {node['id']}")

    def validate_dependencies(self, blueprint: Dict[str, Any]):
        """Ensures all edge targets and sources exist as nodes."""
        node_ids = {node["id"] for node in blueprint.get("graph", {}).get("nodes", [])}
        edges = blueprint.get("graph", {}).get("edges", [])
        
        for edge in edges:
            if edge["from"] not in node_ids:
                raise Exception(f"Edge source '{edge['from']}' not found in nodes.")
            if edge["to"] not in node_ids:
                raise Exception(f"Edge target '{edge['to']}' not found in nodes.")
