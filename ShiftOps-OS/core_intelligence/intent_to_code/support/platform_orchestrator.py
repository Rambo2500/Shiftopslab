from typing import Dict, List, Optional, Any
from pathlib import Path
from intent_to_code.support.platform_graph import PlatformGraph, PlatformNode

class PlatformPlanner:
    """
    Stage 6: Platform Planner.
    Converts high-level platform intent into a PlatformGraph of interconnected systems.
    """
    def plan(self, platform_intent: str) -> PlatformGraph:
        """
        Plans a platform architecture based on user intent.
        For now, uses deterministic templates for common platform types.
        """
        graph = PlatformGraph(goal=platform_intent)

        # Heuristic: simple template selection based on keywords
        intent_lower = platform_intent.lower()
        
        if "logistics" in intent_lower or "saas" in intent_lower:
            graph.add_node(PlatformNode(
                "data_platform",
                "data ingestion and storage platform for logistics telemetry"
            ))
            graph.add_node(PlatformNode(
                "analytics_platform",
                "logistics analytics and KPI computation engine",
                depends_on=["data_platform"]
            ))
            graph.add_node(PlatformNode(
                "api_platform",
                "public API layer for logistics data access",
                depends_on=["analytics_platform"]
            ))
            graph.add_node(PlatformNode(
                "frontend_apps",
                "logistics dashboard and operational monitoring apps",
                depends_on=["api_platform"]
            ))
            graph.add_node(PlatformNode(
                "ai_services",
                "AI-driven route optimization and demand forecasting",
                depends_on=["analytics_platform"]
            ))
        elif "robotics" in intent_lower:
            graph.add_node(PlatformNode(
                "sensor_platform",
                "real-time sensor data ingestion and normalization"
            ))
            graph.add_node(PlatformNode(
                "control_system",
                "autonomous robotics control and path planning",
                depends_on=["sensor_platform"]
            ))
            graph.add_node(PlatformNode(
                "fleet_management",
                "centralized fleet coordination and telemetry",
                depends_on=["sensor_platform"]
            ))
            graph.add_node(PlatformNode(
                "ops_dashboard",
                "robotics operations and maintenance UI",
                depends_on=["fleet_management"]
            ))
        else:
            # Default generic platform
            graph.add_node(PlatformNode("core_service", f"core services for {platform_intent}"))
            graph.add_node(PlatformNode("frontend", "user interface", depends_on=["core_service"]))

        return graph

class PlatformOrchestrator:
    """
    Stage 6: Platform Orchestrator.
    Runs the full architecture engine for each system in a PlatformGraph.
    """
    def __init__(self, architecture_engine: Any):
        self.engine = architecture_engine

    def build_platform(self, platform_graph: PlatformGraph, base_dir: Path = Path("build/platform")) -> Dict[str, Any]:
        """
        Executes the build for an entire platform.
        """
        execution_order = platform_graph.get_execution_order()
        results = {}

        print(f"\n{'='*60}")
        print(f"ORCHESTRATING PLATFORM: {platform_graph.goal}")
        print(f"{'='*60}")

        for node in execution_order:
            print(f"\n>>> Building system: {node.name}")
            print(f"    Intent: {node.system_intent}")
            
            # Here we trigger the existing architecture engine (Planner -> Resolver -> etc)
            # Since we don't have a single 'engine' class yet, we'll need to coordinate
            # the existing Planner and Explorer.
            
            system_build_result = self.engine.run_full_cycle(
                goal=node.name,
                user_request=node.system_intent,
                base_dir=base_dir / node.name
            )
            
            node.system_graph = system_build_result.get("graph")
            results[node.name] = system_build_result

        return {
            "goal": platform_graph.goal,
            "systems": results,
            "mermaid": platform_graph.export_mermaid()
        }
