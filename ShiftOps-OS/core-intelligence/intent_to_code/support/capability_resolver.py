import json
from pathlib import Path
from typing import Dict, Any, List, Set, Optional, Tuple
from intent_to_code.support.system_graph import SystemGraph, SystemNode
from intent_to_code.support.trait_scoring import TraitScorer

class CapabilityResolver:
    """
    Stage 2: Constraint-Driven Capability Resolver.
    Resolves requested capabilities into a complete, 
    topologically sorted dependency graph by satisfying constraints (traits).
    """
    def __init__(self, capabilities_dir: str = "capabilities"):
        self.capabilities_dir = Path(capabilities_dir)
        self.capabilities: Dict[str, Any] = {}
        self.trait_providers: Dict[str, List[str]] = {}
        self.scorer = TraitScorer()
        self._load_capabilities()

    def _load_capabilities(self):
        """Loads all capability definitions and indexes their provided traits."""
        if not self.capabilities_dir.exists():
            return
        for file in self.capabilities_dir.rglob("*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                    if "id" in data:
                        cap_id = data["id"]
                        self.capabilities[cap_id] = data
                        
                        # Index providers
                        provides = data.get("provides", [])
                        for trait in provides:
                            if trait not in self.trait_providers:
                                self.trait_providers[trait] = []
                            self.trait_providers[trait].append(cap_id)
            except Exception:
                pass

    def resolve(self, requested_ids: List[str], goal: str = "unnamed_system", domain_weights: Dict[str, int] = None) -> SystemGraph:
        """
        Expands requested capabilities and returns a SystemGraph object.
        Uses constraint solving to satisfy 'requires' traits.
        Now supports Virtual Capability Synthesis for inferred IDs.
        """
        # --- NEW: Dynamic Ontology Filtering (Constraint Gate) ---
        # Instead of hard-coded DOMAIN_CONSTRAINTS, we now rely on the 
        # higher-level PlanningKernel to provide context-aware filtering 
        # or we use the DomainScout results passed via goal context.
        
        resolved_nodes, edges = self._solve_constraints(requested_ids, goal, domain_weights)
        
        graph = SystemGraph(goal=goal)
        for cap_id in resolved_nodes:
            # Check if it's a real or virtual capability
            if cap_id in self.capabilities:
                cap = self.capabilities[cap_id]
                node_type = cap.get("artifact_type", cap.get("type", "unknown"))
                description = cap.get("description", "")
                cap_class = cap.get("class", "")
                traits = cap.get("provides", [])
                outputs = cap.get("outputs", {})
            else:
                # VIRTUAL SYNTHESIS: Inferred from the ID
                print(f"  [Inference] Synthesizing virtual capability: {cap_id}")
                node_type = "fastapi_service" # Default inferred type
                if "ui" in cap_id or "dashboard" in cap_id: node_type = "dashboard"
                elif "worker" in cap_id or "job" in cap_id: node_type = "worker_service"
                elif "analytics" in cap_id: node_type = "analytics_service"
                
                description = f"Inferred {cap_id} service to satisfy system intent."
                cap_class = "inferred_capability"
                traits = [cap_id]
                outputs = {}

            # Find dependencies for this specific node
            node_deps = [target for src, target in edges if src == cap_id]
            
            node = SystemNode(
                name=cap_id,
                type=node_type,
                description=description,
                depends_on=node_deps,
                capability_class=cap_class,
                traits=traits,
                outputs=outputs
            )
            graph.add_node(node)
            
        return graph

    def _solve_constraints(self, initial_ids: List[str], goal: str = "unnamed_system", domain_weights: Dict[str, int] = None) -> Tuple[Set[str], List[Tuple[str, str]]]:
        """
        Iteratively satisfies constraints until the system is complete.
        Returns (set of capability IDs, list of dependency edges (from_id, to_id)).
        """
        all_ids: Set[str] = set()
        edges: List[Tuple[str, str]] = []
        to_resolve = list(initial_ids)
        
        while to_resolve:
            cap_id = to_resolve.pop(0)
            if cap_id in all_ids:
                continue
                
            # If it's not in our registry, we still include it as a 'Virtual' node
            all_ids.add(cap_id)
            
            if cap_id not in self.capabilities:
                # For virtual nodes, we don't have 'requires' info yet, 
                # so we stop recursion here unless we want to infer requirements too.
                continue
                
            cap = self.capabilities[cap_id]
            
            # Process requirements
            requirements = cap.get("requires", [])
            for req in requirements:
                if isinstance(req, str):
                    # Backward compatibility for direct ID requires
                    edges.append((cap_id, req))
                    to_resolve.append(req)
                elif isinstance(req, dict) and "trait" in req:
                    trait = req["trait"]
                    provider_id = self._find_provider_for_trait(trait, goal, domain_weights)
                    if provider_id:
                        edges.append((cap_id, provider_id))
                        to_resolve.append(provider_id)
                    else:
                        print(f"Warning: No provider found for trait '{trait}' required by '{cap_id}'")
                        
        return all_ids, edges

    def _find_provider_for_trait(self, trait: str, goal: str, domain_weights: Dict[str, int] = None) -> Optional[str]:
        """Finds the best matching capability that provides a given trait."""
        provider_ids = self.trait_providers.get(trait, [])
        if not provider_ids:
            return None
            
        # Get full capability data for each provider
        providers = [self.capabilities[pid] for pid in provider_ids]
        
        # Rank them using the TraitScorer
        ranked = self.scorer.rank_providers(providers, goal, domain_weights)
        
        # Return the ID of the best one
        return ranked[0][0] if ranked else None

    def _get_all_required_ids(self, requested_ids: List[str]) -> Set[str]:
        """Legacy helper for backward compatibility."""
        all_ids, _ = self._solve_constraints(requested_ids)
        return all_ids
