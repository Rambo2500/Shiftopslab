from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# --- 1. THE RESOURCE LAYER (The "Nouns") ---
class Resource(BaseModel):
    """The fundamental physical or digital entities of the system."""
    id: str
    name: str
    category: str # "LABOR", "CAPITAL", "MATERIAL", "ENERGY", "DATA", "LAND"
    capacity: float
    unit_of_measure: str
    current_utilization: float = 0.0
    cost_per_unit: float = 0.0

# --- 2. THE CONSTRAINT LAYER (The "Rules") ---
class Constraint(BaseModel):
    """The boundaries within which the system must operate."""
    id: str
    type: str # "CAPACITY", "REGULATORY", "TIME_WINDOW", "BUDGET", "SAFETY"
    description: str
    threshold: float
    is_hard_stop: bool = True # If True, breaking this stops operations
    governing_body: Optional[str] = None # e.g., "OSHA", "Federal Mandate", "Tribal Council"

# --- 3. THE PROCESS LAYER (The "Verbs") ---
class Process(BaseModel):
    """The transformation of resources over time."""
    id: str
    name: str
    inputs: List[Resource]
    outputs: List[Resource]
    constraints: List[Constraint]
    cycle_time_seconds: float
    variance_buffer: float = 0.0 # Expected deviation

# --- 4. THE ORGANIZATION LAYER (The "Governance") ---
class Governance(BaseModel):
    """How authority and decisions flow."""
    entity_type: str # "CORPORATE", "FEDERAL_AGENCY", "MUNICIPAL", "TRIBAL_SOVEREIGN"
    jurisdiction: str
    compliance_frameworks: List[str]

# --- 5. THE SIGNAL LAYER (The "Nervous System") ---
class SystemSignal(BaseModel):
    """A measurement indicating system health."""
    source_process_id: str
    metric_name: str
    value: float
    timestamp: datetime = Field(default_factory=datetime.now)
    breaches_constraint_id: Optional[str] = None
