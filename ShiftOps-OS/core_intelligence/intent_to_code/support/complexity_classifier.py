import json
from typing import Dict, Any, List, Optional
from intent_to_code.models.gemini_adapter import GeminiAdapter

class ComplexityClassifier:
    """
    Stage 0.5: Complexity Classification.
    Determines if a request is LOW, MEDIUM, or HIGH complexity 
    to guide the architecture synthesis strategy.
    """
    def __init__(self, model_adapter: Optional[GeminiAdapter] = None):
        self.model_adapter = model_adapter or GeminiAdapter()

    def classify(self, user_request: str) -> str:
        """
        Classifies the request complexity: LOW, MEDIUM, or HIGH.
        """
        prompt = f"""
        Act as a Senior Systems Architect.
        Analyze the following user request and classify its required system complexity.
        
        User Request: "{user_request}"
        
        Classification Criteria:
        - LOW: Simple tools, single-file scripts, local data tracking, spreadsheets (e.g., "Excel tracker", "simple script", "one-page app"). 
               If the user explicitly mentions "Excel" or "spreadsheet" for a simple tracking task, it is LOW.
        - MEDIUM: Modular services, basic web apps with databases, internal business tools.
        - HIGH: Enterprise distributed systems, real-time telemetry, global scale, multi-state coordination, complex AI/ML pipelines.
        
        Return ONLY one word: LOW, MEDIUM, or HIGH.
        """
        
        try:
            res = self.model_adapter.generate_text(prompt).strip().upper()
            if "LOW" in res: return "LOW"
            if "HIGH" in res: return "HIGH"
            return "MEDIUM"
        except Exception:
            return "MEDIUM" # Safe default
