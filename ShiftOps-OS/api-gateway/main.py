from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
from datetime import datetime

# Platform Core & Intelligence Imports
from platform_core.schemas import SiteInfo, OperationalSignal, UnifiedFacilityState
from platform_core.ontology.loader import OntologyLoader
from platform_core.ontology.logic import ConstraintParser, StateResolver
from core_intelligence.intent_to_code.support.domain_scout import DomainScout
from core_intelligence.models.gemini_adapter import GeminiAdapter

# Import Engine Services
from engines.facility_engine.production.service import ProductionService
from engines.facility_engine.labor.service import LaborService

load_dotenv()
app = FastAPI(title="ShiftOps-OS API Gateway")

# Initialize Global Managers
gemini = GeminiAdapter()
scout = DomainScout(model_adapter=gemini)
loader = OntologyLoader()
production_service = ProductionService()
labor_service = LaborService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    site: SiteInfo
    signals: List[OperationalSignal]
    industry_pack: str = "hospital_operations_v1" # Example

@app.post("/analyze")
async def analyze_facility(req: AnalysisRequest):
    try:
        # 1. LOAD ONTOLOGY (The Law)
        pack = loader.get_pack(req.industry_pack)
        
        # 2. RUN DETERMINISTIC ENGINES (The Facts)
        # (Simplified production/labor calls)
        production_metrics = production_service.get_current_metrics()
        
        # 3. STATE RESOLUTION (The Spreadsheet)
        # Map symbols from ontology to real state
        resolved_values = StateResolver.resolve_variables(pack, {"production": production_metrics})
        
        # 4. CONSTRAINT VALIDATION (The Judge)
        violations = []
        for constraint in pack.constraints:
            passed = ConstraintParser.evaluate(constraint.expression, resolved_values)
            if not passed:
                violations.append({
                    "id": constraint.id,
                    "expression": constraint.expression,
                    "severity": constraint.severity,
                    "message": constraint.error_message,
                    "offending_value": resolved_values.get(constraint.expression.split()[0])
                })

        # 5. SYNTHESIS (Gemini)
        # Pass the violations to Gemini so it can explain the BLOCK
        prompt = f"""
        Act as the ShiftOps-OS Auditor.
        Site: {req.site.name}. Industry: {req.site.industry}.
        ONTOLOGY VIOLATIONS DETECTED: {violations}
        
        Explain why this facility is in a breach state and suggest an immediate corrective action.
        """
        audit_narrative = gemini.generate_text(prompt)

        return {
            "status": "PASS" if not violations else "BLOCK",
            "violations": violations,
            "audit_explanation": audit_narrative,
            "resolved_state": resolved_values
        }
    except Exception as e:
        print(f"Kernel Panic: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
