import json
from jsonschema import validate, ValidationError
from pathlib import Path
from typing import Dict, Any

class BlueprintValidator:
    def __init__(self, schema_path: str = "contracts/architecture_blueprint.schema.json"):
        self.schema_path = Path(schema_path)
        with open(self.schema_path, "r") as f:
            self.schema = json.load(f)

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
