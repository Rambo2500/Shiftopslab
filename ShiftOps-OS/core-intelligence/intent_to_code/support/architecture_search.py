from typing import List, Dict, Any, Tuple
from intent_to_code.support.system_graph import SystemGraph

class ArchitectureSearchEngine:
    """
    Stage 5.5: Architecture Search Engine.
    Performs multi-step evolution (Monte Carlo / Beam Search style)
    rather than a single-step mutation.
    """
    def __init__(self, explorer, evaluator, max_depth: int = 2, beam_width: int = 5):
        self.explorer = explorer
        self.evaluator = evaluator
        self.max_depth = max_depth
        self.beam_width = beam_width

    def search_yield(self, base_graph: SystemGraph, vision: str = "", complexity: str = "MEDIUM"):
        """
        Generator version of search that yields events for streaming.
        Now complexity-aware to guide the search towards minimalist or enterprise designs.
        """
        best_graph = base_graph
        best_metrics = self.evaluator.evaluate(base_graph, complexity=complexity)
        
        yield {"type": "search_started", "goal": base_graph.goal, "vision": vision, "complexity": complexity}
        
        frontier = [(best_metrics["total_score"], base_graph, best_metrics)]
        total_evaluated = 0

        for depth in range(self.max_depth):
            next_frontier = []
            for _, g, _ in frontier:
                variants = self.explorer.generate_variants(g)
                for v in variants:
                    if v.has_cycles(): continue
                    metrics = self.evaluator.evaluate(v, complexity=complexity)
                    score = metrics["total_score"]
                    
                    next_frontier.append((score, v, metrics))
                    total_evaluated += 1

                    # Stream every evaluation to show "thinking" process
                    yield {
                        "type": "variant_evaluated",
                        "score": score,
                        "metrics": metrics,
                        "depth": depth,
                        "total_evaluated": total_evaluated
                    }
                    
                    if score > best_metrics["total_score"]:
                        best_graph = v
                        best_metrics = metrics
                        yield {
                            "type": "variant_found",
                            "score": score,
                            "metrics": metrics,
                            "graph": v.to_dict(),
                            "mermaid": v.export_mermaid()
                        }
            
            next_frontier.sort(key=lambda x: x[0], reverse=True)
            frontier = next_frontier[:self.beam_width]

        yield {
            "type": "search_complete",
            "best_score": best_metrics["total_score"],
            "total_evaluated": total_evaluated
        }

    def search(self, base_graph: SystemGraph, complexity: str = "MEDIUM") -> Tuple[SystemGraph, Dict[str, Any]]:
        """
        Classic search wrapper for backward compatibility.
        Collects the best results from the search_yield generator.
        """
        best_graph = base_graph
        best_metrics = self.evaluator.evaluate(base_graph, complexity=complexity)
        
        for event in self.search_yield(base_graph, complexity=complexity):
            if event["type"] == "variant_found":
                # The generator yields the full graph dict, we convert back to SystemGraph
                best_graph = SystemGraph.from_dict(event["graph"])
                best_metrics = event["metrics"]
            elif event["type"] == "search_complete":
                # Final safeguard: if no variants were found better than base, 
                # we already have base_graph and base_metrics set.
                pass
        
        return best_graph, best_metrics
