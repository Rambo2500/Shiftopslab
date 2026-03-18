import os
import json
from google import genai
from typing import Optional, Dict, Any, List
from intent_to_code.models.base import ModelAdapter
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class GeminiAdapter(ModelAdapter):
    def __init__(self, api_key: Optional[str] = None):
        project_id = os.getenv("GCP_PROJECT_ID")
        location = os.getenv("GCP_REGION", "us-central1")
        
        if project_id:
            # Vertex AI Client (via ADC)
            self.client = genai.Client(
                vertexai=True,
                project=project_id,
                location=location
            )
            self.model_id = 'gemini-2.0-flash'
        else:
            # Legacy/External Key fallback
            self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
            if self.api_key:
                self.client = genai.Client(api_key=self.api_key)
                self.model_id = 'gemini-2.0-flash-lite'
            else:
                self.client = None

    def call_gemini(self, prompt: str, image_path: Optional[str] = None) -> str:
        """
        Gated AI Call: Performs a single targeted call to Gemini.
        Supports Multi-modal (Vision) if image_path is provided.
        """
        if not self.client:
            return "NO_API_CLIENT_CONFIGURED"

        try:
            contents = [prompt]
            if image_path:
                from pathlib import Path
                img_path = Path(image_path)
                if img_path.exists():
                    # Flash 1.5 handles local files
                    contents.append(img_path)
                else:
                    return f"ERROR: Image path not found: {image_path}"

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents
            )
            return response.text
        except Exception as e:
            return f"ERROR: {str(e)}"


    def decompose_goal(self, goal: str) -> List[str]:
        """
        Stage 1: Recursive Decomposition.
        Uses Gemini to map human goals to capability IDs.
        Now ungated: can suggest new IDs if the registry is insufficient.
        """
        if not self.client:
            # Fallback to legacy keyword matcher for offline/no-key usage
            return self._legacy_decompose_goal(goal)

        prompt = f"""
        Act as the ShiftOps-OS Intent Interpreter.
        Convert the following human system goal into a list of required operational node IDs.
        
        System Goal: "{goal}"
        
        Available Operational Node IDs:
        [process_node, equipment_node, labor_pool, quality_checkpoint, 
        material_buffer, financial_engine, safety_protocol, 
        transport_link, staging_area, packaging_line, maintenance_team]
        
        Requirements:
        1. Use the Registry IDs if they fit.
        2. If the goal requires something not in the registry (e.g., 'oven_control', 'triage_zone'), 
           suggest a new concise ID (e.g., 'thermal_process', 'medical_triage').
        3. DO NOT output software components (like api_service, data_storage) unless explicitly requested. Focus on physical and operational reality.
        
        Return ONLY a JSON list of IDs.
        """
        
        response_text = self.call_gemini(prompt)
        try:
            # Simple cleanup in case LLM adds markdown backticks
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except Exception:
            return self._legacy_decompose_goal(goal)

    def _legacy_decompose_goal(self, goal: str) -> List[str]:
        low_goal = goal.lower()
        capabilities = ["api_service", "dashboard_ui"]
        if any(w in low_goal for w in ["3pl", "fulfillment", "bakery", "logistics", "warehouse"]):
            capabilities.extend(["data_ingestion", "analytics_engine", "ai_reasoning"])
        return list(set(capabilities))

    def design_platform_ecosystem(self, goal: str) -> List[Dict[str, Any]]:
        return [{"name": "core_system", "intent": f"Full system for {goal}", "depends_on": []}]

    def draft_intent(self, user_request: str) -> Dict[str, Any]:
        """
        Translates natural language to an Intent JSON.
        """
        if not self.client:
            return {
                "validated": False,
                "NON_EXECUTABLE_PLAN": True,
                "goal": user_request.split()[0].capitalize() + "_Project",
                "outputs": {"code": {"enabled": True, "type": "dashboard"}},
                "security_envelope": {
                    "network": { "outbound": "ALLOW_TRUSTED" }
                }
            }

        prompt = f"""
        Act as the ShiftOps-OS Platform Planner.
        Convert the user request into a structured Intent JSON.
        
        User Request: "{user_request}"
        
        Requirements:
        1. Set a professional goal name.
        2. Set output type to "dashboard" if a UI is needed.
        3. Include a security_envelope.
        
        Return ONLY valid JSON.
        """
        
        response_text = self.call_gemini(prompt)
        try:
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except Exception:
            return {"error": "Failed to parse intent from AI response."}

    def harvest_context(self, query: str) -> str:
        """
        Stage 2: Context Harvest.
        Uses Gemini to gather contextual information based on a query.
        """
        if not self.client:
            return f"Simulated context for: {query}"
            
        prompt = f"""
        Act as the ShiftOps-OS Context Harvester.
        Provide a concise, high-signal technical summary for the following topic.
        Topic: "{query}"
        
        Focus on system components, data standards, and common architectural patterns.
        """
        return self.call_gemini(prompt)

    def generate_text(self, prompt: str) -> str:
        """
        General purpose text generation (The 'Voice' of the Architect).
        """
        if not self.client:
            return self._legacy_generate_text(prompt)
        return self.call_gemini(prompt)

    def _legacy_generate_text(self, prompt: str) -> str:
        low_prompt = prompt.lower()
        if "3pl" in low_prompt:
            return "A high-scale 3PL fulfillment network."
        if "bakery" in low_prompt:
            return "We are currently moving staff from Line 2 to Line 4 to cover Mike’s call-out and keep the Kroger sourdough run on track. The system has automatically adjusted the oven settings to stop the temperature drift and flagged the grinding conveyor belt for immediate repair. We are prioritizing the 6 AM delivery to avoid any contract penalties."
        return "ShiftOps-OS has created a clear action plan: we are reassigning people to the biggest bottlenecks, stabilizing the machines, and making sure the most important orders get out the door first."

