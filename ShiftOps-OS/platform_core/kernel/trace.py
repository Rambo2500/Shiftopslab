from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel

class ControlTrace(BaseModel):
    """The Universal Forensic Ledger."""
    trace_id: str
    timestamp: datetime = datetime.now()
    actor: str
    intent: Dict[str, Any]
    ontology_id: str
    
    snapshot: Dict[str, float] # The 'Resolved Values'
    violations: List[Dict[str, Any]]
    
    status: str # PASS, BLOCK, OVERRIDE
    execution_acks: List[str] = []

    def to_human_narrative(self) -> str:
        """Converts the raw trace into a clear explanation."""
        msg = f"Trace {self.trace_id}: {self.status}\n"
        msg += f"Industry: {self.ontology_id} | Actor: {self.actor}\n"
        msg += "-" * 30 + "\n"
        
        if self.violations:
            for v in self.violations:
                msg += f"VIOLATION: {v['message']}\n"
                msg += f"Logic: {v['expression']} | Result: {v['offending_value']}\n"
        else:
            msg += "Constraint Check: All rules PASS.\n"
            
        return msg
