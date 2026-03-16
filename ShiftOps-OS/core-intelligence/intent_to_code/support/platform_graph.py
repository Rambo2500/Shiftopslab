from typing import Dict, List, Optional, Any

class PlatformNode:
    """
    Represents a full system within a larger platform.
    A platform node encapsulates a specific system's intent and its dependencies.
    """
    def __init__(self, name: str, system_intent: str, depends_on: List[str] = None):
        self.name = name
        self.system_intent = system_intent
        self.depends_on = depends_on or []
        self.system_graph: Any = None # To be populated by the PlatformOrchestrator

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "system_intent": self.system_intent,
            "depends_on": self.depends_on
        }

class PlatformGraph:
    """
    Manages a collection of PlatformNodes and their interdependencies.
    Provides topological sorting for system-level execution planning.
    """
    def __init__(self, goal: str = "unnamed_platform"):
        self.goal = goal
        self.nodes: Dict[str, PlatformNode] = {}

    def add_node(self, node: PlatformNode):
        self.nodes[node.name] = node

    def get_execution_order(self) -> List[PlatformNode]:
        """Returns a topologically sorted list of PlatformNodes."""
        visited = set()
        temp_stack = set()
        order = []

        def visit(n: str):
            if n in temp_stack:
                raise Exception(f"Circular dependency detected between systems at {n}")
            if n not in visited:
                temp_stack.add(n)
                # Dependencies of n
                node = self.nodes[n]
                for dep in node.depends_on:
                    if dep in self.nodes:
                        visit(dep)
                temp_stack.remove(n)
                visited.add(n)
                order.append(self.nodes[n])

        for node_name in self.nodes:
            if node_name not in visited:
                visit(node_name)
        
        return order

    def export_mermaid(self) -> str:
        """Generates a Mermaid JS flowchart representing the platform architecture."""
        lines = ["graph TD"]
        for node in self.nodes.values():
            clean_name = node.name.replace("-", "_")
            lines.append(f"  {clean_name}[\"{node.name}\"]")
            for dep in node.depends_on:
                clean_dep = dep.replace("-", "_")
                lines.append(f"  {clean_dep} --> {clean_name}")
        return "\n".join(lines)
