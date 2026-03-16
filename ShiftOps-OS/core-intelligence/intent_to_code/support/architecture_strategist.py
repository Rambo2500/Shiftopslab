from typing import List, Dict, Any, Optional
from intent_to_code.support.system_graph import SystemGraph
from intent_to_code.support.architecture_learning import ArchitectureLearningEngine

class ArchitectureStrategist:
    """
    Stage 4.5: Architecture Knowledge Layer.
    Interprets stored architecture patterns to guide the explorer's mutations,
    moving from blind search to strategic exploration.
    Now integrates Stage 5.8: Learning Engine for domain-aware biases.
    """
    def __init__(self, memory):
        self.memory = memory
        self.learning_engine = ArchitectureLearningEngine()

    def suggest_patterns(self, goal: str) -> List[Dict[str, Any]]:
        """Retrieves and ranks historical patterns relevant to the current goal."""
        return self.memory.relevant_patterns(goal)

    def suggest_mutations(self, graph: SystemGraph, goal: str) -> List[str]:
        """
        Analyzes past winning patterns AND learned rules for similar goals
        to recommend mutations.
        Returns a list of mutation strategy names to apply.
        """
        patterns = self.suggest_patterns(goal)
        suggested = set()
        
        # Determine current domain for learning layer
        domain = "default"
        low_goal = goal.lower()
        if "analytics" in low_goal or "warehouse" in low_goal: domain = "analytics"
        elif "finance" in low_goal: domain = "finance"
        elif "robotics" in low_goal or "robot" in low_goal or "drone" in low_goal: domain = "robotics"

        # 1. Baseline mutations we ALWAYS try
        suggested.add("_inject_cache")
        suggested.add("_split_analytics")
        suggested.add("_insert_event_stream")
        suggested.add("_insert_message_queue")
        suggested.add("_separate_api_gateway")

        # 2. Add Biases from Architecture Memory (Passive)
        has_cache = False
        has_stream = False
        for p in patterns:
            nodes = p.get("graph", {}).get("nodes", [])
            for node in nodes:
                name = node.get("name", "")
                if "cache" in name: has_cache = True
                if "stream" in name or "queue" in name: has_stream = True

        if has_cache: suggested.add("_inject_cache")
        if has_stream: suggested.add("_insert_event_stream")

        # 3. Add Biases from Continuous Learning (Active)
        # If the learning engine has seen a specific pattern succeed multiple times,
        # we strictly bias toward it.
        recommendations = self.learning_engine.get_recommendations(domain)
        for rec in recommendations:
            if "cache" in rec: suggested.add("_inject_cache")
            if "queue" in rec or "stream" in rec: suggested.add("_insert_event_stream")
            if "gateway" in rec: suggested.add("_separate_api_gateway")

        return list(suggested)
