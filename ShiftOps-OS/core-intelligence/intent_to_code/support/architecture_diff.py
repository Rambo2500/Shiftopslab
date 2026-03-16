from typing import Dict, Any, List, Set

class ArchitectureDiff:
    """
    Compares two architecture blueprints to identify structural and metric changes.
    """
    def compare(self, baseline: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
        """
        Computes the delta between two blueprints.
        """
        nodes_a = {n["id"]: n for n in baseline.get("graph", {}).get("nodes", [])}
        nodes_b = {n["id"]: n for n in candidate.get("graph", {}).get("nodes", [])}
        
        edges_a = {(e["from"], e["to"]) for e in baseline.get("graph", {}).get("edges", [])}
        edges_b = {(e["from"], e["to"]) for e in candidate.get("graph", {}).get("edges", [])}
        
        added_nodes = [nodes_b[nid] for nid in (nodes_b.keys() - nodes_a.keys())]
        removed_nodes = [nodes_a[nid] for nid in (nodes_a.keys() - nodes_b.keys())]
        
        # Edges
        added_edges = [{"from": f, "to": t} for f, t in (edges_b - edges_a)]
        removed_edges = [{"from": f, "to": t} for f, t in (edges_a - edges_b)]
        
        # Metrics Delta
        eval_a = baseline.get("evaluation", {})
        eval_b = candidate.get("evaluation", {})
        
        metrics_delta = {}
        all_metrics = set(eval_a.keys()) | set(eval_b.keys())
        for m in all_metrics:
            val_a = eval_a.get(m, 0)
            val_b = eval_b.get(m, 0)
            if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                metrics_delta[m] = round(val_b - val_a, 2)

        return {
            "baseline_goal": baseline.get("goal"),
            "candidate_goal": candidate.get("goal"),
            "changes": {
                "added_nodes": added_nodes,
                "removed_nodes": removed_nodes,
                "added_edges": added_edges,
                "removed_edges": removed_edges
            },
            "metrics_delta": metrics_delta,
            "summary": self._generate_summary(added_nodes, removed_nodes, metrics_delta)
        }

    def _generate_summary(self, added, removed, delta) -> str:
        summary = f"Evolution Result: Fitness {'increased' if delta.get('fitness_score', 0) > 0 else 'decreased'} by {abs(delta.get('fitness_score', 0))}. "
        if added:
            summary += f"Added {len(added)} components (e.g., {added[0]['id']}). "
        if removed:
            summary += f"Optimized out {len(removed)} components. "
        return summary
