from typing import Dict, Any, List, Tuple

class TraitScorer:
    """
    Stage 2.5: Trait Intelligence Layer.
    Ranks capability providers based on how well their performance traits 
    (latency, throughput, cost) align with the system's high-level goal.
    """
    
    TRAIT_VALUES = {
        "exceptional": 4,
        "high": 3,
        "medium": 2,
        "low": 1,
        "poor": 0
    }
    
    def score_provider(self, provider_data: Dict[str, Any], goal: str, domain_weights: Dict[str, int] = None) -> float:
        """
        Calculates a fitness score for a provider based on its traits 
        and the target system goal.
        """
        traits = provider_data.get("traits", {})
        if not traits:
            return 0.0

        # If weights aren't provided, use a flat default
        weights = domain_weights or {
            "throughput": 1,
            "latency": 1,
            "consistency": 1,
            "cost": 1
        }
        
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

    def rank_providers(self, providers: List[Dict[str, Any]], goal: str, domain_weights: Dict[str, int] = None) -> List[Tuple[str, float]]:
        """Ranks a list of capability providers by score."""
        results = []
        for p in providers:
            score = self.score_provider(p, goal, domain_weights)
            results.append((p["id"], score))
        
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results
