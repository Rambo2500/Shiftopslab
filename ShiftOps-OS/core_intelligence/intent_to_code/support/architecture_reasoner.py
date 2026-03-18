from typing import List, Dict
from intent_to_code.support.system_graph import SystemGraph, SystemNode

class ArchitectureReasoner:
    """
    Stage 4: Architecture Reasoning Layer.
    Applies architectural logic and patterns to refine the capability graph.
    """
    
    def refine(self, graph: SystemGraph) -> SystemGraph:
        print("\n[Architecture Reasoner] Analyzing system graph...")
        
        # 1. Enforce pattern: worker -> queue -> analytics (decoupling)
        self._decouple_compute_layers(graph)
        
        # 2. Ensure data pipeline: inject storage if analytics exist but no storage
        self._ensure_data_persistence(graph)

        # 3. AI boundaries: ensure AI reasoning is decoupled from the main API
        self._enforce_ai_boundaries(graph)

        return graph

    def _decouple_compute_layers(self, graph: SystemGraph):
        """
        If a worker directly depends on an analytics engine, inject a message queue.
        """
        has_worker = "data_ingestion" in graph.nodes
        has_analytics = "analytics_engine" in graph.nodes
        
        # simplified check for demonstration
        if has_worker and has_analytics:
            # Check if queue already exists
            if "message_queue" not in graph.nodes:
                print("  -> Rule Applied: Decoupling worker and analytics with message_queue")
                queue_node = SystemNode(
                    name="message_queue",
                    type="queue_service",
                    description="Message queue for asynchronous processing",
                    depends_on=[]
                )
                graph.add_node(queue_node)
                
                # Update dependencies (worker -> queue, analytics_engine -> queue)
                graph.nodes["data_ingestion"].depends_on.append("message_queue")
                # Remove direct coupling if it existed (not in our current default, but good practice)
                if "analytics_engine" in graph.nodes["data_ingestion"].depends_on:
                    graph.nodes["data_ingestion"].depends_on.remove("analytics_engine")

    def _ensure_data_persistence(self, graph: SystemGraph):
        """
        If analytics or API exists, ensure there is a data storage layer.
        """
        needs_storage = any(n in graph.nodes for n in ["analytics_engine", "api_service"])
        if needs_storage and "data_storage" not in graph.nodes:
            print("  -> Rule Applied: Injecting data_storage for persistence")
            storage_node = SystemNode(
                name="data_storage",
                type="database_service",
                description="Persistent data storage",
                depends_on=[]
            )
            graph.add_node(storage_node)
            
            if "api_service" in graph.nodes:
                graph.nodes["api_service"].depends_on.append("data_storage")
            if "analytics_engine" in graph.nodes:
                graph.nodes["analytics_engine"].depends_on.append("data_storage")

    def _enforce_ai_boundaries(self, graph: SystemGraph):
        """
        Ensure AI reasoning isn't a direct blocking dependency for the API.
        """
        pass # To be implemented as we add more complex AI patterns
