from typing import Dict, Any, List, Optional
import copy

class ArchitectureSimulator:
    """
    Simulates operational scenarios on an architecture blueprint.
    """
    def __init__(self, blueprint: Dict[str, Any]):
        self.blueprint = copy.deepcopy(blueprint)
        self.nodes = self.blueprint.get("graph", {}).get("nodes", [])
        self.edges = self.blueprint.get("graph", {}).get("edges", [])
        self.evaluation = self.blueprint.get("evaluation", {})

    def simulate_node_failure(self, node_id: str) -> Dict[str, Any]:
        """
        Simulates the failure of a specific node and its impact on dependent nodes.
        """
        failed_nodes = {node_id}
        
        # Propagate failure through edges
        changed = True
        while changed:
            changed = False
            for edge in self.edges:
                if edge["from"] in failed_nodes and edge["to"] not in failed_nodes:
                    failed_nodes.add(edge["to"])
                    changed = True
                    
        impacted_percentage = len(failed_nodes) / len(self.nodes) if self.nodes else 0
        
        return {
            "scenario": f"Failure of node: {node_id}",
            "failed_nodes": list(failed_nodes),
            "system_impact": f"{round(impacted_percentage * 100, 2)}% of system impacted",
            "recovery_time_estimate": f"{round(len(failed_nodes) * 0.5, 1)}s",
            "new_resilience_score": round(self.evaluation.get("resilience_score", 0) * (1 - impacted_percentage), 2)
        }

    def simulate_latency_spike(self, node_id: str, delay_ms: int) -> Dict[str, Any]:
        """
        Simulates increased latency on a specific node.
        """
        current_latency = self.evaluation.get("latency_score", 0)
        # Latency propagates downstream
        return {
            "scenario": f"Latency spike on: {node_id} (+{delay_ms}ms)",
            "impacted_node": node_id,
            "new_latency_score": round(current_latency + (delay_ms / 100), 2),
            "critical_path_impact": "Downstream nodes delayed"
        }

    def simulate_throughput_test(self, multiplier: float) -> Dict[str, Any]:
        """
        Simulates a load increase.
        """
        cost = self.evaluation.get("cost_score", 0)
        return {
            "scenario": f"Throughput test at {multiplier}x load",
            "new_cost_score": round(cost * multiplier, 2),
            "status": "scaling required" if multiplier > 2.0 else "stable"
        }
