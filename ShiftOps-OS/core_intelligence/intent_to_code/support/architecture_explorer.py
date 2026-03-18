import re
from copy import deepcopy
from typing import List, Dict, Any
from intent_to_code.support.system_graph import SystemGraph, SystemNode
from intent_to_code.support.architecture_memory import ArchitectureMemory
from intent_to_code.support.architecture_strategist import ArchitectureStrategist

class ArchitectureExplorer:
    """
    Stage 5/7: Architecture Exploration Engine.

    Generates mutated variants of a SystemGraph so the
    ArchitectureEvaluator can score them.
    Integrates Stage 4.5 Strategist to guide search with winning patterns.
    """

    def __init__(self, memory_dir: str = "architecture_memory"):
        self.memory = ArchitectureMemory(memory_dir)
        self.strategist = ArchitectureStrategist(self.memory)

    def generate_variants(self, graph: SystemGraph, domain: str = "default") -> List[SystemGraph]:
        """
        Produces a list of alternative architectures based on the input graph.
        New pipeline: base_graph + suggested patterns -> suggested mutations -> evaluate -> best
        """
        # Reload memory to catch any newly stored ones during this session
        self.memory.load_patterns()

        # 1. Start with the base graph
        candidates = [deepcopy(graph)]
        
        # 2. Ask strategist for relevant past patterns
        patterns = self.strategist.suggest_patterns(graph.goal)
        candidates.extend(self.seed_from_patterns(patterns))

        # 3. Ask strategist for the best mutations to try
        mutation_names = self.strategist.suggest_mutations(graph, graph.goal, domain=domain)

        # 4. Mutate ALL of them using suggested strategies
        all_variants = []
        for c in candidates:
            all_variants.append(c) # Include the unmutated version
            all_variants.extend(self.apply_mutations(c, mutation_names, domain=domain))

        return all_variants

    def seed_from_patterns(self, patterns: List[Dict[str, Any]]) -> List[SystemGraph]:
        """Retrieves and adapts winning patterns suggested by strategist."""
        seeds = []
        for p in patterns:
            try:
                # Seed explorer with a high-scoring past architecture
                seed = SystemGraph.from_dict(p["graph"])
                seeds.append(seed)
            except Exception:
                pass
        return seeds

    def apply_mutations(self, graph: SystemGraph, mutation_names: List[str], domain: str = "default") -> List[SystemGraph]:
        """Dynamically applies suggested mutations."""
        mutations = []
        for name in mutation_names:
            if hasattr(self, name):
                mutator = getattr(self, name)
                # Note: individual mutators might need to be domain-aware in the future
                mutated_graph = mutator(graph)
                if mutated_graph:
                    mutations.append(mutated_graph)
        return mutations


    # ----------------------------
    # Mutation Strategies
    # ----------------------------

    def _inject_cache(self, graph: SystemGraph) -> SystemGraph:
        g = deepcopy(graph)
        if "api_service" in g.nodes and "cache_layer" not in g.nodes:
            cache = SystemNode(
                name="cache_layer",
                type="cache_service",
                description="Caching layer to reduce load on analytics",
                depends_on=[]
            )
            g.add_node(cache)
            # API depends on cache
            g.nodes["api_service"].depends_on.append("cache_layer")
            return g
        return None

    def _split_analytics(self, graph: SystemGraph) -> SystemGraph:
        g = deepcopy(graph)
        if "analytics_engine" in g.nodes:
            # Create a router and two workers to replace the single engine
            router = SystemNode(
                name="analytics_router",
                type="worker_service",
                description="Routes analytics jobs to worker cluster",
                depends_on=["api_service"]
            )
            worker_a = SystemNode(
                name="analytics_worker_a",
                type="worker_service",
                description="Analytics worker node",
                depends_on=["analytics_router"]
            )
            worker_b = SystemNode(
                name="analytics_worker_b",
                type="worker_service",
                description="Analytics worker node",
                depends_on=["analytics_router"]
            )

            g.add_node(router)
            g.add_node(worker_a)
            g.add_node(worker_b)

            # Remove the original engine
            if "analytics_engine" in g.nodes:
                del g.nodes["analytics_engine"]
                # Clean up edges (simplified for demonstration)
                g.edges = [e for e in g.edges if e[1] != "analytics_engine" and e[0] != "analytics_engine"]

            return g
        return None

    def _insert_event_stream(self, graph: SystemGraph) -> SystemGraph:
        g = deepcopy(graph)
        # Only inject if we don't already have a queue/stream (avoiding redundancy)
        if "message_queue" not in g.nodes and "event_stream" not in g.nodes:
            stream = SystemNode(
                name="event_stream",
                type="stream_service",
                description="Event streaming layer",
                depends_on=[]
            )
            g.add_node(stream)
            if "data_ingestion" in g.nodes:
                g.nodes["data_ingestion"].depends_on.append("event_stream")
            if "sensor_ingestion" in g.nodes:
                g.nodes["sensor_ingestion"].depends_on.append("event_stream")
            return g
        return None

    def _insert_message_queue(self, graph: SystemGraph) -> SystemGraph:
        g = deepcopy(graph)
        if "message_queue" not in g.nodes and "event_stream" not in g.nodes:
            queue = SystemNode(
                name="message_queue",
                type="queue_service",
                description="Message queue for asynchronous processing",
                depends_on=[]
            )
            g.add_node(queue)
            # Find any ingestion/compute node to attach it to
            if "sensor_ingestion" in g.nodes:
                g.nodes["sensor_ingestion"].depends_on.append("message_queue")
            elif "data_ingestion" in g.nodes:
                g.nodes["data_ingestion"].depends_on.append("message_queue")
            return g
        return None

    def _separate_api_gateway(self, graph: SystemGraph) -> SystemGraph:
        g = deepcopy(graph)
        if "api_service" in g.nodes and "api_gateway" not in g.nodes:
            gateway = SystemNode(
                name="api_gateway",
                type="gateway_service",
                description="External API gateway",
                depends_on=[]
            )
            g.add_node(gateway)
            g.nodes["api_service"].depends_on.append("api_gateway")
            return g
        return None
