from typing import Dict, Any, List, Set, Optional

class SystemNode:
    def __init__(self, name: str, type: str, description: str = "", depends_on: List[str] = None, capability_class: str = "", compatible_with: List[str] = None, traits: List[str] = None, outputs: Dict[str, List[str]] = None):
        self.name = name
        self.type = type
        self.description = description
        self.depends_on = depends_on or []
        self.capability_class = capability_class
        self.compatible_with = compatible_with or []
        self.traits = traits or [type] # Default trait is just the type
        self.outputs = outputs or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.name,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "depends_on": self.depends_on,
            "capability_class": self.capability_class,
            "compatible_with": self.compatible_with,
            "traits": self.traits,
            "outputs": self.outputs
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemNode':
        return cls(
            name=data.get("id", data.get("name", "unnamed")),
            type=data["type"],
            description=data.get("description", ""),
            depends_on=data.get("depends_on", []),
            capability_class=data.get("capability_class", ""),
            compatible_with=data.get("compatible_with", []),
            traits=data.get("traits", []),
            outputs=data.get("outputs", {})
        )

class SystemGraph:
    """
    Represents the system architecture as a Directed Acyclic Graph (DAG).
    Provides methods for topological sorting, cycle detection, and parallel execution planning.
    """
    def __init__(self, goal: str):
        self.goal = goal
        self.nodes: Dict[str, SystemNode] = {}
        self.edges: List[tuple] = []

    def add_node(self, node: SystemNode):
        self.nodes[node.name] = node
        for dep in node.depends_on:
            self.edges.append((dep, node.name))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [{"from": e[0], "to": e[1]} for e in self.edges]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemGraph':
        graph = cls(goal=data.get("goal", "unnamed_graph"))
        for node_data in data.get("nodes", []):
            graph.add_node(SystemNode.from_dict(node_data))
        return graph

    def has_cycles(self) -> bool:
        """
        Cycle-Proof Graph Engine: Ensures the architecture is a valid DAG.
        Returns True if a dependency cycle is detected.
        """
        visited = set()
        stack = set()

        def visit(n: str) -> bool:
            if n in stack:
                return True # Cycle detected
            if n not in visited:
                stack.add(n)
                deps = self.nodes[n].depends_on
                for dep in deps:
                    if dep in self.nodes:
                        if visit(dep):
                            return True
                stack.remove(n)
                visited.add(n)
            return False

        for node_name in self.nodes:
            if node_name not in visited:
                if visit(node_name):
                    return True
        return False

    def get_topologically_sorted(self) -> List[SystemNode]:
        """Simple DFS-based topological sort."""
        visited = set()
        temp_stack = set()
        order = []

        def visit(n: str):
            if n in temp_stack:
                raise Exception(f"Circular dependency detected at {n}")
            if n not in visited:
                temp_stack.add(n)
                # Dependencies of n
                deps = self.nodes[n].depends_on
                for dep in deps:
                    if dep in self.nodes:
                        visit(dep)
                temp_stack.remove(n)
                visited.add(n)
                order.append(self.nodes[n])

        for node_name in self.nodes:
            if node_name not in visited:
                visit(node_name)
        
        return order

    def to_list(self) -> List[Dict[str, Any]]:
        """Returns the topologically sorted component list as dicts."""
        return [node.to_dict() for node in self.get_topologically_sorted()]

    def export_mermaid(self) -> str:
        """
        Generates a Mermaid JS class diagram or flowchart representing the architecture.
        """
        lines = ["graph TD"]
        for node in self.nodes.values():
            # Define node with type info
            clean_name = node.name.replace("-", "_")
            lines.append(f"  {clean_name}[\"{node.name} <br/> ({node.type})\"]")
            
            # Define edges
            for dep in node.depends_on:
                clean_dep = dep.replace("-", "_")
                lines.append(f"  {clean_dep} --> {clean_name}")
        
        return "\n".join(lines)
