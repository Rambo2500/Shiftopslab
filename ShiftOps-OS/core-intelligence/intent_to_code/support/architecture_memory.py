import json
from pathlib import Path
import hashlib
from typing import List, Dict, Any

class ArchitectureMemory:
    """
    Stage 7: Architecture Memory.
    Persists winning architectures to a library of "patterns" or "openings".
    """
    def __init__(self, memory_dir: str = "architecture_memory"):
        self.memory_dir = Path(memory_dir)
        self.pattern_dir = self.memory_dir / "patterns"
        self.pattern_dir.mkdir(parents=True, exist_ok=True)

    def _hash_graph(self, graph) -> str:
        """Generates a unique hash for a graph based on its structure."""
        data = json.dumps(graph.to_dict(), sort_keys=True)
        return hashlib.md5(data.encode()).hexdigest()

    def store_pattern(self, goal: str, graph, score: float):
        """Stores a winning architecture in the pattern library."""
        pattern_id = self._hash_graph(graph)

        pattern = {
            "pattern_id": pattern_id,
            "goal": goal,
            "score": score,
            "graph": graph.to_dict()
        }

        path = self.pattern_dir / f"{pattern_id}.json"
        with open(path, "w") as f:
            json.dump(pattern, f, indent=2)

    def load_patterns(self) -> List[Dict[str, Any]]:
        """Loads all stored patterns from the library."""
        patterns = []
        for file in self.pattern_dir.glob("*.json"):
            try:
                with open(file, "r") as f:
                    patterns.append(json.load(f))
            except Exception:
                pass
        return patterns

    def relevant_patterns(self, goal: str) -> List[Dict[str, Any]]:
        """Filters patterns based on keyword similarity to the target goal."""
        import re
        patterns = self.load_patterns()
        
        def tokenize(text):
            return set(re.findall(r'\w+', text.lower()))

        goal_words = tokenize(goal)
        results = []

        for p in patterns:
            pattern_goal = p.get("goal", "").lower()
            pattern_words = tokenize(pattern_goal)
            
            overlap = len(goal_words & pattern_words)
            if overlap > 0:
                results.append(p)
                
        # Sort by score descending (best patterns first)
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results

    def get_relevant_patterns(self, goal: str) -> List[Dict[str, Any]]:
        """Alias for relevant_patterns for backward compatibility."""
        return self.relevant_patterns(goal)
