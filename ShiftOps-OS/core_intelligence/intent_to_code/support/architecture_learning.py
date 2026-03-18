import json
from pathlib import Path
from typing import Dict, Any, List
from intent_to_code.support.system_graph import SystemGraph

class ArchitectureLearningEngine:
    """
    Stage 5.8: Continuous Learning Engine.
    Observes winning architectures, extracts "successful" patterns 
    (mutations/components that lead to high scores), and persists them
    as architecture rules to inform the Strategist.
    """
    def __init__(self, rules_path: str = "architecture_rules.json"):
        self.rules_path = Path(rules_path)
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        if self.rules_path.exists():
            try:
                with open(self.rules_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "component_biases": {}, # domain -> {component_id: count}
            "successful_mutations": {}, # domain -> {mutation_name: success_count}
            "high_score_threshold": 8.0
        }

    def learn_from_result(self, goal: str, graph: SystemGraph, evaluation: Dict[str, Any], domain: str = "default"):
        """
        Analyzes a completed architecture run and updates learned rules
        if the architecture performed well.
        """
        score = evaluation.get("total_score", 0)
        if score < self.rules["high_score_threshold"]:
            return # Only learn from high-quality designs

        # 1. Update component biases for this domain
        if domain not in self.rules["component_biases"]:
            self.rules["component_biases"][domain] = {}
        
        for node in graph.nodes.values():
            name = node.name
            # Track common helpful components (e.g., cache, queue)
            if any(k in name for k in ["cache", "queue", "stream", "gateway"]):
                current_count = self.rules["component_biases"][domain].get(name, 0)
                self.rules["component_biases"][domain][name] = current_count + 1

        # 2. Persist the updated rules
        self._save_rules()
        print(f"[Architecture Learning] Extracted insights from '{goal}' (Score: {score:.2f})")

    def _save_rules(self):
        with open(self.rules_path, "w") as f:
            json.dump(self.rules, f, indent=2)

    def get_recommendations(self, domain: str) -> List[str]:
        """Returns recommended components/mutations for a given domain."""
        domain_biases = self.rules["component_biases"].get(domain, {})
        # Sort components by their success count
        sorted_biases = sorted(domain_biases.items(), key=lambda x: x[1], reverse=True)
        return [b[0] for b in sorted_biases if b[1] > 1] # Only recommend if seen at least twice
