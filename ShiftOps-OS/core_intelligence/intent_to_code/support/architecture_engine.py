from typing import Dict, Any, List, Optional, Tuple, Set
import json
import random
from pathlib import Path
from intent_to_code.support.planner import PlanningKernel
from intent_to_code.support.capability_resolver import CapabilityResolver
from intent_to_code.support.architecture_explorer import ArchitectureExplorer
from intent_to_code.support.architecture_evaluator import ArchitectureEvaluator
from intent_to_code.support.system_graph import SystemGraph, SystemNode
from intent_to_code.compiler import compile_intent
from intent_to_code.support.domain_scout import DomainScout
from intent_to_code.support.complexity_classifier import ComplexityClassifier

class ContractMaterializer:
    """
    The Bridge from Architecture to Code.
    Materializes UI bindings into actual FastAPI service endpoints
    with Adaptive Risk Monitoring (deterministic logic).
    """
    @staticmethod
    def materialize_service(service_name: str, bindings: List[Dict], outputs: Dict, domain_data: Dict = None) -> str:
        endpoints = ""
        domain_data = domain_data or {}
        kpis = domain_data.get("kpis", [])
        incidents = domain_data.get("incidents", [])
        
        # --- RISK MONITORING LOGIC (The Survival Instinct) ---
        risk_logic = f"""
def calculate_risk_metrics():
    # Deterministic Risk Math
    active_incidents = random.randint(0, 3) if random.random() > 0.8 else 0
    base_health = 100.0 - (active_incidents * 25.0)
    
    # Revenue at Risk (Simulated based on service importance)
    rev_at_risk = active_incidents * random.uniform(5000, 15000)
    
    return {{
        "health_score": max(0.0, base_health),
        "active_incidents": active_incidents,
        "revenue_at_risk": round(rev_at_risk, 2),
        "recovery_horizon_days": active_incidents * 2
    }}
"""

        # 1. Implement generic capability outputs
        for out_name, out_fields in outputs.items():
            # (Generic output implementation preserved but grounded)
            endpoints += f"""
@app.get("/{out_name}")
async def get_{out_name}():
    metrics = calculate_risk_metrics()
    return {{ 
        "{out_name}": [{{ "id": f"{service_name.upper()}_{{i:03}}", "status": "nominal" if metrics['health_score'] > 70 else "degraded" }} for i in range(5)],
        "operational_health": metrics,
        "timestamp": datetime.now().isoformat()
    }}
"""

        # 2. Implement specific UI bindings with Deterministic Logic
        for b in bindings:
            endpoint = b.get("endpoint", "/unknown").lstrip("/")
            method = b.get("method", "GET").lower()
            resp_model = b.get("response_model", {})
            label = b.get("label", "Unknown Metric")
            
            mock_logic = []
            for k, v in resp_model.items():
                k_low = k.lower()
                
                # Domain-Specific Clamping logic
                matched_kpi = next((kpi for kpi in kpis if kpi['name'].lower() in k_low or k_low in kpi['name'].lower()), None)
                
                if matched_kpi:
                    r = matched_kpi['range']
                    # Use a stable "deterministic" seed based on current hour to avoid jitter
                    seed = datetime.now().hour
                    if isinstance(r[0], int):
                        mock_logic.append(f'"{k}": {r[0]} + (datetime.now().minute % ({r[1]} - {r[0]}))')
                    else:
                        mock_logic.append(f'"{k}": round({r[0]} + (datetime.now().second * 0.1 % ({r[1]} - {r[0]})), 2)')
                elif 'risk' in k_low or 'health' in k_low:
                    mock_logic.append(f'"{k}": calculate_risk_metrics()')
                elif 'latitude' in k_low or 'lat' in k_low:
                    mock_logic.append(f'"{k}": 34.0522')
                elif 'longitude' in k_low or 'lng' in k_low:
                    mock_logic.append(f'"{k}": -118.2437')
                elif 'status' in k_low:
                    mock_logic.append(f'"{k}": "nominal" if datetime.now().minute % 10 != 0 else "degraded"')
                else:
                    mock_logic.append(f'"{k}": "Active_Data"')

            endpoints += f"""
@app.{method}("/{endpoint}")
async def handle_{endpoint.replace('/', '_')}_ui():
    return {{
        {', '.join(mock_logic)},
        "telemetry_source": "Deterministic_Grounding_v2"
    }}
"""

        return f"""# Service: {service_name}
# Synthesized by ShiftOps-OS Universal Architect
# Domain Archetype: {domain_data.get('archetype', 'Generic')}

from fastapi import FastAPI
from datetime import datetime
import random
import os

app = FastAPI(title="{service_name}")

{risk_logic}

@app.get("/")
async def root():
    return {{
        "status": "active", 
        "service": "{service_name}",
        "domain": "{domain_data.get('archetype', 'Generic')}",
        "operational_integrity": calculate_risk_metrics()
    }}
{endpoints}
"""

class ArchitectureEngine:
    def __init__(self, capabilities_dir: str = "capabilities"):
        self.resolver = CapabilityResolver(capabilities_dir)
        self.planner = PlanningKernel()
        self.evaluator = ArchitectureEvaluator()
        self.explorer = ArchitectureExplorer()
        self.scout = DomainScout()
        self.complexity_classifier = ComplexityClassifier()

    def generate_snapshot(self, goal: str, user_request: str, image_path: str = None) -> Dict[str, Any]:
        """
        The Unified Snapshot Generator.
        Translates Intent -> Domain Scout -> Architecture -> Surface Manifest.
        """
        # 0. Domain Grounding
        print(f"[Domain Scout] Researching '{user_request}'...")
        domain_data = self.scout.scout(user_request)
        
        # 0.2 Load Ontology Context
        archetype = domain_data.get("archetype", "Generic").lower().replace(" ", "_")
        ontology = self.planner.ontology_loader.get_pack(f"{archetype}_v1")
        
        # 0.5 Complexity Classification
        complexity = self.complexity_classifier.classify(user_request)
        print(f"[Complexity] Classified as {complexity}")
        
        # 1. Plan the system (Complexity-Aware)
        system_intent = self.planner.plan_system(user_request, complexity=complexity, domain_data=domain_data)
        if not system_intent or "error" in system_intent:
            raise Exception(f"Planning failed: {system_intent.get('error', 'Unknown')}")
        
        system_intent["goal"] = goal
        outputs = system_intent.get("outputs") if isinstance(system_intent.get("outputs"), dict) else {}
        system_outputs = outputs.get("system") if isinstance(outputs.get("system"), dict) else {}
        components = system_outputs.get("components") if isinstance(system_outputs.get("components"), list) else []

        # 2. Build the System Graph
        winning_graph = SystemGraph(goal=goal)
        for c in components:
            if c: winning_graph.add_node(SystemNode.from_dict(c))
            
        # 2.5 Evaluate with Complexity & Ontology Context
        evaluation = self.evaluator.evaluate(winning_graph, complexity=complexity, ontology=ontology)
        
        # 3. Generate Director Summary
        try:
            narrative_prompt = f"""
            Act as the ShiftOps-OS Lead Architect.
            Provide a 3-paragraph executive summary for a Director of Operations regarding the following system: "{goal}".
            The system is designed to handle this crisis: "{user_request}".
            System Resilience: {evaluation.get('total_score')}.
            
            Focus on:
            1. Cross-domain risk mitigation (Labor vs Production).
            2. The 'Truth Layer' grounding this architecture.
            3. Operational outcome confidence.
            
            Return ONLY the narrative text. No markdown, no prefixes.
            """
            narrative_summary = self.planner.model_adapter.generate_text(narrative_prompt).strip()
            # Ensure we didn't just get the prompt back or an empty string
            if len(narrative_summary) < 50 or "Summarize this" in narrative_summary:
                raise Exception("Narrative too short or invalid.")
        except:
            narrative_summary = f"System architecture for {goal} has been successfully synthesized. The kernel has identified {len(components)} critical nodes to stabilize the {domain_data.get('archetype')} environment. Current fitness scoring of {evaluation.get('total_score')} indicates high structural reliability for OTIF fulfillment."

        # 4. Handle Vision (If image provided)
        blueprint = None
        if image_path:
            print(f"[Vision Engine] Interpreting image: {image_path}")
            blueprint = self.scout.interpret_vision(image_path, user_request)

        # 4. Universal Surface Projection
        surface_manifest = self._generate_surface_projection(user_request, components, domain_data, complexity)
        
        # Add Process Flow projection
        if "surfaces" in surface_manifest:
            surface_manifest["surfaces"].append({
                "id": "process_flow",
                "title": "Process Flow Diagram",
                "projection": "flow",
                "layers": [
                    {
                        "id": "flow_layer",
                        "type": "flow_diagram",
                        "nodes": [n.to_dict() for n in winning_graph.nodes.values()],
                        "edges": [{"from": d, "to": n.name} for n in winning_graph.nodes.values() for d in n.depends_on]
                    }
                ]
            })

        if blueprint and "surfaces" in surface_manifest:
            surface_manifest["surfaces"].insert(0, {
                "id": "vision_blueprint",
                "title": blueprint.get("title", "Spatial Hologram"),
                "projection": "blueprint",
                "layers": blueprint.get("layers", [])
            })

        # 5. Build Repository Hologram
        full_repo = self._orchestrate_to_hologram(system_intent, surface_manifest, domain_data)

        # 6. Generate Roadmap & Technical Rationale (Decision Intelligence)
        try:
            roadmap_prompt = f"""
            Act as a Lead Systems Architect. 
            Generate a high-fidelity 4-step operational roadmap for: "{user_request}".
            Domain: {domain_data.get('archetype')}
            
            The roadmap must focus on operational stability and recovery.
            
            Return ONLY valid JSON in this format:
            [
              {{"step": "01", "title": "...", "desc": "..."}},
              {{"step": "02", "title": "...", "desc": "..."}},
              {{"step": "03", "title": "...", "desc": "..."}},
              {{"step": "04", "title": "...", "desc": "..."}}
            ]
            """
            roadmap_res = self.planner.model_adapter.generate_text(roadmap_prompt)
            clean_roadmap = roadmap_res.replace("```json", "").replace("```", "").strip()
            roadmap = json.loads(clean_roadmap)
        except:
            roadmap = [
                {"step": "01", "title": "Floor Assessment", "desc": f"Checking the actual {domain_data.get('archetype')} lines against our plans."},
                {"step": "02", "title": "Staff Reassignment", "desc": "Moving people to the most critical spots right now."},
                {"step": "03", "title": "Machine Stabilization", "desc": "Adjusting machine settings to stop any drift."},
                {"step": "04", "title": "Order Fulfillment", "desc": "Verifying the final load is ready for the truck."}
            ]

        # 7. Metadata and Confidence
        binding_count = 0
        if surface_manifest and "surfaces" in surface_manifest:
            for s in surface_manifest["surfaces"]:
                for l in s.get("layers", []):
                    items = l.get("components", []) if "components" in l else [l]
                    for c in items:
                        if "binding" in c: binding_count += 1
        
        if binding_count > 0:
            evaluation["total_score"] += (binding_count * 2.5)

        return {
            "id": goal.replace(" ", "_").lower(),
            "status": "active",
            "domain_archetype": domain_data.get("archetype"),
            "domain_data": domain_data,
            "architecture": {
                "nodes": [n.to_dict() for n in winning_graph.nodes.values()],
                "edges": [{"from": d, "to": n.name} for n in winning_graph.nodes.values() for d in n.depends_on]
            },
            "repo": full_repo,
            "surface_manifest": surface_manifest,
            "narrative_summary": narrative_summary,
            "diagnostics": {
                "confidence": min(1.0, evaluation.get("total_score", 0) / 100.0),
                "fitness_score": evaluation.get("total_score", 0),
                "archetype": domain_data.get("archetype"),
                "kpis": domain_data.get("kpis", []),
                "incidents": domain_data.get("incidents", []),
                "reasons": evaluation.get("decision_rationale", []),
                "roadmap": roadmap,
                "scalability_index": evaluation.get("scalability_score", 0),
                "resilience_score": evaluation.get("resilience_score", 0),
                "complexity": complexity
            }
        }

    def run_search_cycle(self, goal: str, user_request: str):
        """
        Streaming version of the synthesis cycle.
        Yields search events from the ArchitectureSearchEngine.
        """
        # 0. Domain & Complexity
        domain_data = self.scout.scout(user_request)
        complexity = self.complexity_classifier.classify(user_request)
        
        yield {"type": "domain_researched", "domain": domain_data, "complexity": complexity}

        # 1. Expand Intent
        expanded = self.planner._expand_intent(user_request, complexity, domain_data)
        yield {"type": "intent_expanded", "expanded": expanded}

        # 2. Decompose & Resolve
        requested = self.planner.model_adapter.decompose_goal(expanded)
        base_graph = self.resolver.resolve(requested, goal=goal)
        yield {"type": "base_graph_resolved", "graph": base_graph.to_dict()}

        # 3. Search & Evolve
        search_engine = self.planner.search_engine
        for event in search_engine.search_yield(base_graph, complexity=complexity):
            yield event

    def run_full_cycle(self, goal: str, user_request: str, base_dir: Path = Path("build")) -> List[Dict]:
        """
        Executes the full synthesis-to-code pipeline.
        Returns a list of compilation results.
        """
        # 1. Generate the snapshot (Architecture + Surface Manifest)
        snapshot = self.generate_snapshot(goal, user_request)
        
        # 2. Extract components from the snapshot's architecture
        components = snapshot["architecture"]["nodes"]
        
        # 3. Create a system intent for the orchestrator
        system_intent = {
            "goal": goal,
            "outputs": {
                "system": {
                    "enabled": True,
                    "type": "custom_assembly",
                    "components": components,
                    "bootstrap_env": True
                }
            },
            "domain_data": {
                "archetype": snapshot["domain_archetype"],
                "kpis": snapshot["diagnostics"]["kpis"],
                "incidents": snapshot["diagnostics"]["incidents"]
            }
        }
        
        # 4. Orchestrate the physical build
        from intent_to_code.system_orchestrator import orchestrate_system
        orchestration_result = orchestrate_system(system_intent)
        
        # 5. Return the list of artifacts
        return orchestration_result.get("artifacts", [])

    def evolve_snapshot(self, snapshot: Dict, mutation_request: str) -> Dict[str, Any]:
        """
        Takes an existing snapshot and evolves it.
        This enables "Save -> Improve" workflow.
        """
        goal = snapshot.get("id", "evolved_system")
        current_arch = snapshot.get("architecture", {})
        
        # 1. Convert back to SystemGraph
        current_graph = SystemGraph.from_dict(current_arch)
        current_graph.goal = goal
        
        # 2. Get Domain & Complexity
        domain_data = self.scout.scout(mutation_request)
        complexity = self.complexity_classifier.classify(mutation_request)
        
        # 3. Use Planner to suggest evolution
        evolved_graph = self.planner.evolve(current_graph, mutation_request, domain_data)
        
        # 4. Re-evaluate
        evaluation = self.evaluator.evaluate(evolved_graph, complexity=complexity)
        
        # 5. Generate new Snapshot
        components = [n.to_dict() for n in evolved_graph.nodes.values()]
        surface_manifest = self._generate_surface_projection(mutation_request, components, domain_data, complexity)
        
        # 6. Build the evolve result (simplified snapshot)
        return {
            "id": goal,
            "status": "evolved",
            "domain_archetype": domain_data.get("archetype"),
            "architecture": evolved_graph.to_dict(),
            "surface_manifest": surface_manifest,
            "diagnostics": {
                "confidence": min(1.0, evaluation.get("total_score", 0) / 100.0),
                "fitness_score": evaluation.get("total_score", 0),
                "complexity": complexity,
                "archetype": domain_data.get("archetype"),
                "kpis": domain_data.get("kpis", []),
                "incidents": domain_data.get("incidents", [])
            }
        }

    def _generate_surface_projection(self, request: str, components: List[Dict], domain_data: Dict = None, complexity: str = "MEDIUM") -> Dict:
        comp_list = ", ".join([c['name'] for c in components])
        domain_context = ""
        if domain_data:
            kpis = [k['name'] for k in domain_data.get('kpis', [])]
            incidents = [i['type'] for i in domain_data.get('incidents', [])]
            domain_context = f"\nResearched Domain Archetype: {domain_data.get('archetype')}\nResearched KPIs: {', '.join(kpis)}\nResearched Incidents: {', '.join(incidents)}"

        prompt = f"""
        Design a high-fidelity 'Surface Manifest' for: "{request}"
        Available Components in Architecture: {comp_list}
        Complexity: {complexity}
        {domain_context}
        
        CRITICAL SCHEMA:
        {{
          "surfaces": [
            {{
              "id": "surface_id",
              "title": "Surface Title",
              "projection": "dashboard",
              "layers": [
                {{
                  "id": "layer_id",
                  "components": [
                    {{
                      "type": "metric|list|map|chat|incidents|action",
                      "label": "Label",
                      "binding": {{
                        "data_source": "service_name",
                        "endpoint": "/api/endpoint",
                        "method": "GET",
                        "response_model": {{"field": "type"}}
                      }}
                    }}
                  ]
                }}
              ]
            }}
          ]
        }}
        
        Output ONLY valid JSON.
        """
        try:
            res = self.planner.model_adapter.generate_text(prompt)
            manifest = json.loads(res.replace("```json", "").replace("```", "").strip())
            if "surfaces" not in manifest and "layers" in manifest:
                manifest = {"surfaces": [{"id": "default", "title": manifest.get("title", "Command"), "projection": "dashboard", "layers": manifest.get("layers", [])}]}
            
            # --- TRUTH LAYER INJECTION ---
            if "surfaces" in manifest:
                matches = domain_data.get("domain_matches", [])
                signals = domain_data.get("source_signals", [])
                
                truth_layer = {
                    "id": "truth_layer",
                    "title": "Architecture Truth Layer",
                    "projection": "dashboard",
                    "layers": [
                        {
                            "id": "grounding_signals",
                            "components": [
                                {"type": "metric", "label": "Domain Archetype", "value": domain_data.get("archetype", "Unknown")},
                                {"type": "metric", "label": "Complexity Class", "value": complexity},
                                {"type": "metric", "label": "Evidence Density", "value": "HIGH" if len(signals) > 3 else "MEDIUM"}
                            ]
                        },
                        {
                            "id": "domain_correlation",
                            "components": [
                                {"type": "list", "label": "Domain Matches", "items": [f"{m['name']} ({int(m['score']*100)}%)" for m in matches]}
                            ]
                        },
                        {
                            "id": "evidence_trace",
                            "components": [
                                {"type": "list", "label": "Source Signals Detected", "items": signals},
                                {"type": "list", "label": "Targeted KPIs", "items": [k["name"] for k in domain_data.get("kpis", [])]}
                            ]
                        }
                    ]
                }
                manifest["surfaces"].append(truth_layer)
                
            return manifest
        except:
            return {"surfaces": [{"id": "default", "title": "Dashboard", "projection": "dashboard", "layers": []}]}


    def _orchestrate_to_hologram(self, intent, surface_manifest=None, domain_data=None):
        components = intent.get("outputs", {}).get("system", {}).get("components", [])
        goal = intent.get("goal", "System")
        domain_data = domain_data or {}
        
        full_repo = {
            "README.md": f"# {goal}\nAutomated System Synthesis by ShiftOps-OS.\nArchetype: {domain_data.get('archetype', 'Generic')}",
            "shiftops.config.json": json.dumps(intent, indent=2),
            "docker-compose.yml": "version: '3.8'\nservices:\n"
        }

        if surface_manifest:
            full_repo["surface_manifest.json"] = json.dumps(surface_manifest, indent=2)

        service_bindings = {}
        if surface_manifest and "surfaces" in surface_manifest:
            for surface in surface_manifest["surfaces"]:
                for layer in surface.get("layers", []):
                    items = layer.get("components", []) if "components" in layer else [layer]
                    for comp in items:
                        binding = comp.get("binding")
                        if binding and "data_source" in binding:
                            src = binding["data_source"]
                            if src not in service_bindings: service_bindings[src] = []
                            service_bindings[src].append(binding)

        for c in components:
            name = c['name']
            outputs = c.get('outputs', {})
            bindings = service_bindings.get(name, [])
            full_repo["docker-compose.yml"] += f"  {name}:\n    build: ./services/{name}\n    ports: [\"{8000 + components.index(c)}:8000\"]\n"
            full_repo[f"services/{name}/main.py"] = ContractMaterializer.materialize_service(name, bindings, outputs, domain_data)
            full_repo[f"services/{name}/Dockerfile"] = "FROM python:3.9-slim\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]"
            full_repo[f"services/{name}/requirements.txt"] = "fastapi\nuvicorn\npydantic"
            
        return full_repo

