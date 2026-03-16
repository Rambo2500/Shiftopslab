from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class EntitySpec(BaseModel):
    """Defines a type of thing the system can control."""
    type: str
    state_fields: List[str]
    description: Optional[str] = None

class ConstraintSpec(BaseModel):
    """A rule that must be true for a state transition to be valid."""
    id: str
    expression: str # e.g., "count(patient.unit == 'ICU') < ICU_CAPACITY"
    severity: str = "SAFETY" # SAFETY, REGULATORY, SYSTEM, OPTIMIZATION
    error_message: str

class ActuatorMapping(BaseModel):
    """Connects an entity transition to a specific hardware or software subsystem."""
    entity_type: str
    transition_type: str
    connector_id: str # e.g., "sql_scheduler", "plc_line_b"

class IndustryPack(BaseModel):
    """A Loadable Ontology Module (LOM)."""
    ontology_id: str
    version: str
    entities: Dict[str, EntitySpec]
    constraints: List[ConstraintSpec]
    actuators: List[ActuatorMapping]
    metadata: Dict[str, Any] = Field(default_factory=dict)
