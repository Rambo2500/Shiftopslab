from typing import Dict, Any
import json

class DSLConverter:
    """
    Converts Architecture Blueprints (JSON) to Markdown DSL for AI reasoning
    and vice versa. This is the 'reader' on both ends.
    """

    @staticmethod
    def blueprint_to_dsl(blueprint: Dict[str, Any]) -> str:
        goal = blueprint.get("goal", "Unnamed System")
        evaluation = blueprint.get("evaluation", {})
        graph = blueprint.get("graph", {})
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])

        dsl = [
            f"SYSTEM: {goal}",
            f"FITNESS: {evaluation.get('fitness_score', 0)}",
            "",
            "ENTITIES"
        ]

        for node in nodes:
            node_id = node.get("id") or node.get("name")
            node_type = node.get("type", "unknown")
            dsl.append(f"- {node_id} ({node_type})")

        dsl.append("")
        dsl.append("FLOW")
        for edge in edges:
            dsl.append(f"{edge.get('from')} \u2192 {edge.get('to')}")

        return "\n".join(dsl)

    @staticmethod
    def dsl_to_intent(dsl: str) -> Dict[str, Any]:
        """
        Parses the Markdown DSL back into a structured intent for the engine.
        """
        lines = dsl.splitlines()
        intent = {
            "goal": "Parsed System",
            "components": [],
            "flows": []
        }

        current_section = None
        for line in lines:
            line = line.strip()
            if not line: continue

            if line.startswith("SYSTEM:"):
                intent["goal"] = line.replace("SYSTEM:", "").strip()
            elif line == "ENTITIES":
                current_section = "entities"
            elif line == "FLOW":
                current_section = "flow"
            elif current_section == "entities" and line.startswith("- "):
                # Match "name (type)"
                import re
                match = re.match(r"- (.*) \((.*)\)", line)
                if match:
                    intent["components"].append({
                        "name": match.group(1).strip(),
                        "type": match.group(2).strip()
                    })
            elif current_section == "flow" and "\u2192" in line:
                parts = line.split("\u2192")
                intent["flows"].append({
                    "from": parts[0].strip(),
                    "to": parts[1].strip()
                })

        return intent
