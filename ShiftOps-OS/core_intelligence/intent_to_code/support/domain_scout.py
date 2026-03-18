import json
from typing import Dict, Any, List, Optional
from intent_to_code.models.gemini_adapter import GeminiAdapter

class DomainScout:
    """
    Stage 0: Domain Grounding.
    Researches the industry/domain to find realistic KPIs, ranges, and event archetypes.
    """
    def __init__(self, model_adapter: Optional[GeminiAdapter] = None):
        self.model_adapter = model_adapter or GeminiAdapter()

    def scout(self, user_request: str) -> Dict[str, Any]:
        """
        Runs a high-fidelity research phase on the requested domain.
        Ensures the system identifies the specific 'Physics' of the environment.
        """
        prompt = f"""
        Act as a Senior ShiftOps Systems Scientist.
        Research the following operational domain request: "{user_request}"
        
        Your goal is to define the 'Deterministic Physics' of this specific environment.
        
        If the request involves a BAKERY:
        - Archetype: Bakery Science
        - KPIs: Hydration %, Proofing Time (min), Oven Temp (F), Scrap Rate (%), OTIF %.
        - Incidents: Yeast Inactivity, Divider Jam, Thermal Drift, Labor Shortfall.
        
        If the request involves LABOR, SCHEDULING, or HR:
        - Archetype: Workforce Ops
        - KPIs: Coverage Ratio (%), Avg Fatigue Index, Certification Density (%), OT Hours.
        - Incidents: Call-out, Skill Gap, Shift Overlap Conflict, Compliance Breach.

        If the request involves SIX SIGMA, QUALITY, MINITAB, or STATISTICAL CONTROL:
        - Archetype: Black Belt
        - KPIs: Cpk Index, P-Value (Normality), Sigma Level, Pareto 80/20 Ratio.
        - Incidents: Non-Normal Drift, Capability Failure, Root Cause Ambiguity.
        
        If the request involves DISASTER RECOVERY/FEMA:
        - Archetype: Disaster Recovery
        - KPIs: Evacuation Rate (%), Triage Throughput (p/hr), Resource Depletion (%), Comms Stability (%).
        - Incidents: Bridge Failure, Levee Breach, Supply Chain Severance, Grid Blackout.
        
        If the request involves HOSPITAL/LOGISTICS:
        - Archetype: Hospital Logistics
        - KPIs: ER Load Index, Bed Turnover (min), Staff Fatigue Rate (%), EHR Latency (ms).
        - Incidents: Surge Overflow, System Sync Lag, Oxygen Manifold Failure, HIPAA Breach.
        
        For ANY other domain, identify the industry standard KPIs and realistic ranges.
        
        Return ONLY valid JSON in this format:
        {{
          "archetype": "Specific Domain Name",
          "domain_matches": [
            {{"name": "Specific Industry", "score": 0.99}}
          ],
          "source_signals": ["term1", "term2"],
          "kpis": [
            {{"name": "...", "range": [min, max], "unit": "...", "description": "..."}}
          ],
          "incidents": [
            {{"type": "...", "severity_levels": ["low", "medium", "high", "critical"]}}
          ]
        }}
        """
        
        try:
            res = self.model_adapter.generate_text(prompt)
            # Cleanup
            clean_res = res.replace("```json", "").replace("```", "").strip()
            # Basic validation
            data = json.loads(clean_res)
            if "archetype" not in data or len(data.get("kpis", [])) < 2:
                raise ValueError("Incomplete domain data.")
            return data
        except Exception as e:
            print(f"[DomainScout] LLM failed or returned invalid JSON. Using heuristic matching...")
            # Heuristic Fallback
            req_low = user_request.lower()
            if "bakery" in req_low or "oven" in req_low or "dough" in req_low:
                return {
                    "archetype": "Bakery Science",
                    "domain_matches": [{"name": "Industrial Food Production", "score": 0.95}],
                    "source_signals": ["bakery_physics_detected"],
                    "kpis": [
                        {"name": "Proofing Stability", "range": [90, 100], "unit": "%", "description": "Percentage of dough batches meeting hydration spec."},
                        {"name": "Oven Efficiency", "range": [85, 98], "unit": "%", "description": "Thermal consistency across bake cycle."},
                        {"name": "OTIF fulfillment", "range": [95, 100], "unit": "%", "description": "On-time in-full delivery rate."}
                    ],
                    "incidents": [
                        {"type": "Thermal Fluctuation", "severity_levels": ["medium", "high", "critical"]},
                        {"type": "Mechanical Jam", "severity_levels": ["high", "critical"]},
                        {"type": "Labor Shortfall", "severity_levels": ["medium", "high"]}
                    ]
                }
            
            # Default to slightly better than 'General Operations'
            return {
                "archetype": "Critical Infrastructure",
                "domain_matches": [{"name": "System Logistics", "score": 0.8}],
                "source_signals": ["generic_failover"],
                "kpis": [
                    {"name": "Throughput", "range": [0, 5000], "unit": "units/hr", "description": "Standard flow rate."},
                    {"name": "Operational Health", "range": [0, 100], "unit": "%", "description": "Overall system stability."}
                ],
                "incidents": [
                    {"type": "Node Failure", "severity_levels": ["high", "critical"]},
                    {"type": "Performance Lag", "severity_levels": ["low", "medium"]}
                ]
            }

    def interpret_vision(self, image_path: str, context: str) -> Dict[str, Any]:
        """
        Translates an image (photo/sketch) into a Blueprint JSON for the Hologram.
        """
        prompt = f"""
        Act as a ShiftOps-OS Vision Engineer.
        Analyze this image in the context of: "{context}"
        
        Generate a Spatial Blueprint JSON for the holographic projector.
        Identify zones, machines, walls, or sensors.
        
        Return ONLY valid JSON:
        {{
          "title": "Blueprint Title",
          "layers": [
            {{
              "id": "l1",
              "elements": [
                {{"type": "zone|rect|part", "label": "...", "x": 0-800, "y": 0-500, "w": 0-200, "h": 0-200, "r": 0-50}}
              ]
            }}
          ]
        }}
        """
        try:
            # Multi-modal call
            res = self.model_adapter.call_gemini(prompt, image_path=image_path)
            clean_res = res.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_res)
        except:
            return {"title": "Default Blueprint", "layers": []}

