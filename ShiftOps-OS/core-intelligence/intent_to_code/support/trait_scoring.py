from typing import Dict, Any, List, Tuple

class TraitScorer:
    """
    Stage 2.5: Trait Intelligence Layer.
    Ranks capability providers based on how well their performance traits 
    (latency, throughput, cost) align with the system's high-level goal.
    """
    
    # Weights for different goal archetypes
    GOAL_WEIGHTS = {
        "analytics": {
            "throughput": 10,
            "latency": 2,
            "consistency": 1,
            "cost": 5
        },
        "realtime": {
            "latency": 10,
            "throughput": 5,
            "consistency": 8,
            "cost": 2
        },
        "disaster_response": {
            "latency": 10,
            "throughput": 10,
            "consistency": 10,
            "resilience": 10,
            "cost": 1
        },
        "finance": {
            "consistency": 10,
            "latency": 5,
            "throughput": 2,
            "cost": 2
        },
        "default": {
            "throughput": 1,
            "latency": 1,
            "consistency": 1,
            "cost": 1
        }
    }

    # Value mappings for traits
    TRAIT_VALUES = {
        "high": 3,
        "medium": 2,
        "low": 1,
        "strong": 3,
        "eventual": 1
    }

    def score_provider(self, provider_data: Dict[str, Any], goal: str) -> float:
        """
        Calculates a fitness score for a provider based on its traits 
        and the target system goal.
        """
        traits = provider_data.get("traits", {})
        if not traits:
            return 0.0

        # Determine the goal archetype
        archetype = "default"
        low_goal = goal.lower()
        if "disaster" in low_goal or "emergency" in low_goal:
            archetype = "disaster_response"
        elif "analytics" in low_goal or "warehouse" in low_goal:
            archetype = "analytics"
        elif "realtime" in low_goal or "stream" in low_goal:
            archetype = "realtime"
        elif "finance" in low_goal or "transaction" in low_goal or "risk" in low_goal:
            archetype = "finance"

        weights = self.GOAL_WEIGHTS.get(archetype, self.GOAL_WEIGHTS["default"])
        total_score = 0.0

        for trait_name, trait_val in traits.items():
            if trait_name in weights:
                # Map symbolic value (high/low) to numeric
                numeric_val = self.TRAIT_VALUES.get(trait_val, 0)
                
                # Special case: cost is usually better if low, unless we ignore it
                if trait_name == "cost":
                    # Lower cost (1) gets higher relative score than high cost (3)
                    # Score = Weight * (4 - NumericVal)
                    total_score += weights[trait_name] * (4 - numeric_val)
                else:
                    total_score += weights[trait_name] * numeric_val

        return total_score

    def rank_providers(self, providers: List[Dict[str, Any]], goal: str) -> List[Tuple[str, float]]:
        """Ranks a list of capability providers by score."""
        results = []
        for p in providers:
            score = self.score_provider(p, goal)
            results.append((p["id"], score))
        
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results
