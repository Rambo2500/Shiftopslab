"""
Execution router (deterministic).

Selects and runs execution paths explicitly requested by intent.
No defaults. No inference.
"""

from typing import Dict, List
from pathlib import Path

from intent_to_code.batches.batch_22_passive_harvester import run_batch_22_passive_harvester
from intent_to_code.batches.batch_11_guidance_producer import run_batch_11_guidance_producer

from intent_to_code.executors.guidance_admissibility_gate import apply_guidance_admissibility_gate
from intent_to_code.executors.guidance_executor import execute_guidance
from intent_to_code.executors.guidance_exporter import export_guidance_markdown

from intent_to_code.support.audit_trace import write_audit_trace
from intent_to_code.compiler import compile_intent
from intent_to_code.system_orchestrator import orchestrate_system


def route_execution(intent: Dict, preview: bool = False) -> List[Dict]:
    """
    Route execution based on explicit intent outputs.

    If preview=True:
      - No execution occurs
      - Returns a deterministic plan of what WOULD run
    """
    results: List[Dict] = []

    outputs = intent.get("outputs", {})

    # ============================================================
    # Guidance pipeline:
    # Batch 22 (harvest) -> Batch 11 (produce)
    # -> Admissibility Gate -> render -> export
    # ============================================================
    if outputs.get("guidance") is True:
        # Build deterministic context
        context = {
            "intent": intent
        }

        # ---- Batch 22: passive multi-engine harvest (additive) ----
        context = run_batch_22_passive_harvester(context)

        # ---- Batch 11: guidance production (additive) ----
        context = run_batch_11_guidance_producer(context)

        guidance_payload = context.get("guidance_payload")

        # ---- Admissibility Gate: hard reject non-guidance bullets ----
        filtered_payload, rejection_report = apply_guidance_admissibility_gate(
            guidance_payload
        )

        # ---- Audit (facts only, append-only) ----
        write_audit_trace({
            "stage": "guidance_admissibility",
            "status": "completed",
            "kept": rejection_report.get("kept"),
            "dropped": rejection_report.get("dropped"),
            "rejections_total": len(rejection_report.get("rejections", [])),
            # cap to prevent log explosion
            "rejections": rejection_report.get("rejections", [])[:50]
        })

        guidance_payload = filtered_payload

        if preview:
            results.append({
                "type": "guidance_pipeline",
                "action": "would_render_and_export",
                "export_path": "outputs/guidance/plan_*.md"
            })
        else:
            rendered = execute_guidance(guidance_payload)
            path = export_guidance_markdown(
                rendered,
                "plan_small_automation_project.md"
            )
            results.append({
                "type": "guidance_markdown",
                "path": path
            })

    # ============================================================
    # Optional compiler path (unchanged)
    # ============================================================
    code_request = outputs.get("code", {})
    if code_request.get("enabled") is True:
        if preview:
            results.append({
                "type": "compiler",
                "action": "would_compile_code"
            })
        else:
            results.append({
                "type": "compiler",
                "result": compile_intent(intent)
            })

    # ============================================================
    # Optional system orchestration path (multi-artifact)
    # ============================================================
    system_request = outputs.get("system", {})
    if system_request.get("enabled") is True:
        if preview:
            results.append({
                "type": "system_orchestrator",
                "action": f"would_orchestrate_system: {system_request.get('type', 'unspecified')}"
            })
        else:
            from intent_to_code.support.architecture_engine import ArchitectureEngine
            engine = ArchitectureEngine()
            
            # Use ArchitectureEngine for dynamic planning and evolution
            goal = intent.get("goal", "unnamed_system")
            system_result = engine.run_full_cycle(
                goal=goal,
                user_request=goal, # Using goal as the request for the planner
                base_dir=Path("build") / goal
            )
            
            results.append({
                "type": "system_orchestrator",
                "result": system_result
            })

    # ============================================================
    # Optional platform orchestration path (multi-system)
    # ============================================================
    platform_request = outputs.get("platform", {})
    if platform_request.get("enabled") is True:
        if preview:
            results.append({
                "type": "platform_orchestrator",
                "action": f"would_orchestrate_platform: {intent.get('goal', 'unnamed_platform')}"
            })
        else:
            from intent_to_code.support.platform_orchestrator import PlatformOrchestrator
            from intent_to_code.support.platform_strategy import PlatformStrategyEngine
            from intent_to_code.support.architecture_engine import ArchitectureEngine

            engine = ArchitectureEngine()
            orchestrator = PlatformOrchestrator(engine)
            planner = PlatformStrategyEngine()

            platform_graph = planner.design_ecosystem(intent.get("goal", "unnamed_platform"))
            platform_result = orchestrate_platform(orchestrator, platform_graph)            
            results.append({
                "type": "platform_orchestrator",
                "result": platform_result
            })

    return results

def orchestrate_platform(orchestrator, platform_graph) -> Dict:
    """
    Wrapper for building a platform.
    """
    return orchestrator.build_platform(platform_graph)


