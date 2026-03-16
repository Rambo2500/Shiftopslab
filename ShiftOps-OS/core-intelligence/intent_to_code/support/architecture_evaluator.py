from typing import Dict, Any, List
from intent_to_code.support.system_graph import SystemGraph

class ArchitectureEvaluator:
    """
    Stage 5.5: Architecture Evaluator.
    The "Brain" that scores system graphs based on architectural metrics.
    Provides the objective function for architecture exploration.
    """

    def evaluate(self, graph: SystemGraph, complexity: str = "MEDIUM") -> Dict[str, Any]:
        """
        Computes a comprehensive architectural fitness score for a graph.
        Now complexity-aware to reward minimalism where appropriate.
        """
        import random
        metrics = {
            "depth": self._calculate_depth(graph),
            "parallelism": self._calculate_parallelism(graph),
            "coupling": self._calculate_coupling(graph),
            "resilience": self._calculate_resilience(graph),
            "node_count": len(graph.nodes)
        }

        # Domain-agnostic metrics based on capability classes
        classes = {node.capability_class for node in graph.nodes.values() if hasattr(node, "capability_class")}
        
        if "control" in classes:
            metrics["control_latency"] = self._calculate_depth(graph) * 1.5
        if "transport" in classes or "interface" in classes:
            metrics["data_throughput"] = len([n for n in graph.nodes.values() if n.capability_class in ("transport", "compute", "interface")]) * 10.0
        if "storage" in classes:
            metrics["state_consistency"] = self._calculate_coupling(graph) * 0.8 # arbitrary heuristic

        # New platform scores
        metrics["scalability_score"] = round(metrics["parallelism"] * 1.2 - metrics["coupling"] * 0.5, 2)
        metrics["cost_score"] = round(metrics["node_count"] * 1.0 + metrics.get("data_throughput", 0) * 0.02, 2)
        metrics["resilience_score"] = round(metrics["resilience"], 2)
        metrics["latency_score"] = round(metrics.get("control_latency", metrics["depth"] * 1.0), 2)

        # Decision Intelligence
        metrics["commercial_summary"] = self._generate_commercial_summary(metrics)
        metrics["decision_rationale"] = self._generate_decision_rationale(graph, metrics, complexity)

        # Calculate weighted total score
        # High parallelism and resilience are good (+).
        # High depth (latency) and coupling (complexity) are penalized (-).
        total_score = (
            (metrics.get("parallelism", 0) * 2.0) +
            (metrics.get("resilience", 0) * 1.5) -
            (metrics.get("depth", 0) * 1.0) -
            (metrics.get("coupling", 0) * 5.0) # High penalty for high edge density
        )
        
        # --- COMPLEXITY ADAPTATION LAYER ---
        if complexity == "LOW":
            # For LOW complexity, we reward minimalism and low node counts.
            if metrics["node_count"] <= 5:
                total_score += 20.0 # Huge bonus for lean systems
            elif metrics["node_count"] > 10:
                total_score -= (metrics["node_count"] * 2.0) # Heavy penalty for bloat
            
            # Penalize heavy components if not requested
            node_types = {n.type for n in graph.nodes.values()}
            if "message_queue" in node_types or "stream_processor" in node_types:
                total_score -= 15.0 # Queues are overkill for small scripts
        
        # Add class-based metric impact
        if "data_throughput" in metrics:
            total_score += metrics["data_throughput"] * 0.1
        if "control_latency" in metrics:
            total_score -= metrics["control_latency"] * 0.5
        if "state_consistency" in metrics:
            total_score += metrics["state_consistency"] * 1.0

        # Inject a small amount of "Design Innovation" entropy (0.01 to 0.5)
        entropy = random.uniform(0.01, 0.49)
        metrics["total_score"] = round(total_score + entropy, 2)
        return metrics

    def _generate_commercial_summary(self, metrics: Dict) -> str:
        """Translates technical scores into a professional executive summary."""
        resilience = metrics.get("resilience_score", 0)
        cost = metrics.get("cost_score", 0)
        
        status = "High Stability" if resilience > 2 else "Lean Implementation"
        risk = "Low Operational Risk" if cost < 15 else "Complex Infrastructure"
        
        return f"{status} | {risk}"

    def _generate_decision_rationale(self, graph: SystemGraph, metrics: Dict, complexity: str = "MEDIUM") -> List[str]:
        """Provides professional reasoning for the architectural choices."""
        rationale = []
        node_types = {n.type for n in graph.nodes.values()}
        
        if complexity == "LOW" and metrics["node_count"] <= 5:
            rationale.append("Minimalist direct-path architecture chosen for cost-optimized initial deployment.")
        
        if "message_queue" in node_types or "stream_processor" in node_types:
            if complexity == "LOW":
                rationale.append("WARNING: Complex asynchronous decoupling detected in a LOW complexity request.")
            else:
                rationale.append("Asynchronous decoupling via message queues selected for high-throughput stability.")
        
        if "cache_layer" in node_types or "redis" in node_types:
            rationale.append("Integrated caching implemented to optimize for low-latency distribution access.")
            
        if metrics.get("parallelism", 0) > 3 and complexity != "LOW":
            rationale.append("Highly parallelized ingestion layer designed for global scale concurrency.")
            
        if not rationale:
            rationale.append("Standard modular architecture baseline.")
            
        return rationale


    def _calculate_depth(self, graph: SystemGraph) -> int:
        """
        Measures the longest dependency chain (critical path).
        Higher depth usually means higher system latency.
        """
        if not graph.nodes:
            return 0
            
        # Simple longest path estimation using topological sort
        sorted_nodes = graph.get_topologically_sorted()
        depths = {node.name: 1 for node in sorted_nodes}
        
        for node in sorted_nodes:
            for dep in node.depends_on:
                if dep in depths:
                    depths[node.name] = max(depths[node.name], depths[dep] + 1)
        
        return max(depths.values()) if depths else 0

    def _calculate_parallelism(self, graph: SystemGraph) -> int:
        """
        Measures how many nodes can be built/executed concurrently.
        """
        if not graph.nodes:
            return 0
        # Roots (nodes with no dependencies) are immediately parallelizable
        roots = [n for n in graph.nodes.values() if not n.depends_on]
        return len(roots)

    def _calculate_coupling(self, graph: SystemGraph) -> float:
        """
        Measures edge density. High coupling makes systems harder to maintain.
        """
        node_count = len(graph.nodes)
        if node_count <= 1:
            return 0.0
        edge_count = len(graph.edges)
        return edge_count / node_count

    def _calculate_resilience(self, graph: SystemGraph) -> float:
        """
        Heuristic for resilience based on redundancy or decoupling (e.g. presence of queues/buffers).
        """
        resilience = 0.0
        for node in graph.nodes.values():
            # Reward decoupling patterns
            if "queue" in node.type or "stream" in node.type or "cache" in node.type:
                resilience += 1.0
            # Reward persistence layers
            if "database" in node.type or "storage" in node.type:
                resilience += 0.5
        return resilience
