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
        Runs a research phase on the requested domain.
        Now returns grounding signals for the Truth Layer.
        """
        prompt = f"""
        Act as a ShiftOps Systems Analyst.
        Research the operational domain for this request: "{user_request}"
        
        Identify the 'Physics' of this system:
        1. Common KPIs (Key Performance Indicators).
        2. Realistic numeric ranges for each KPI.
        3. Operational exception/incident types specific to this domain.
        4. Archetype category.
        
        Also provide 'Grounding Signals' for traceability:
        - domain_matches: Top 3 industry/domain matches with confidence scores (0.0 to 1.0).
        - source_signals: List of technical patterns or terminology detected that triggered this domain recognition.
        
        Return ONLY valid JSON in this format:
        {{
          "archetype": "...",
          "domain_matches": [
            {{"name": "...", "score": 0.95}},
            ...
          ],
          "source_signals": ["...", "..."],
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
            return json.loads(clean_res)
        except Exception as e:
            # Robust Fallback for Generic Operations
            return {
                "archetype": "General Operations",
                "domain_matches": [
                    {"name": "General Operations", "score": 1.0}
                ],
                "source_signals": ["generic_request"],
                "kpis": [
                    {"name": "Throughput", "range": [0, 10000], "unit": "units"},
                    {"name": "Efficiency", "range": [0, 100], "unit": "%"}
                ],
                "incidents": [
                    {"type": "System Latency", "severity_levels": ["low", "medium", "high"]},
                    {"type": "Data Gap", "severity_levels": ["low", "high"]}
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

