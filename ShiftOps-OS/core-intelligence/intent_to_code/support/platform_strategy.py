from typing import Dict, Any, Optional
from intent_to_code.support.platform_graph import PlatformGraph, PlatformNode
from intent_to_code.models.gemini_adapter import GeminiAdapter

class PlatformStrategyEngine:
    """
    Stage 6.5: Platform Strategy Engine.
    Designs multi-system ecosystems by leveraging LLM reasoning to decompose
    a massive enterprise goal into distinct, inter-dependent platforms.
    """
    def __init__(self, model_adapter: Optional[GeminiAdapter] = None):
        self.model_adapter = model_adapter or GeminiAdapter()

    def design_ecosystem(self, platform_intent: str) -> PlatformGraph:
        """
        Uses reasoning to architect an entire platform ecosystem, 
        returning a connected PlatformGraph.
        """
        print(f"[Platform Strategy] Designing ecosystem for: '{platform_intent}'...")
        graph = PlatformGraph(goal=platform_intent)
        
        # 1. Ask the reasoning layer to design the system domains
        systems = self.model_adapter.design_platform_ecosystem(platform_intent)
        
        # 2. Build the PlatformGraph
        for sys in systems:
            node = PlatformNode(
                name=sys["name"],
                system_intent=sys["intent"],
                depends_on=sys.get("depends_on", [])
            )
            graph.add_node(node)
            print(f"  -> Identified Domain: {node.name} (Depends on: {node.depends_on})")
            
        return graph
