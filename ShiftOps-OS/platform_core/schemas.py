from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class SiteInfo(BaseModel):
    """Generic Operational Site Definition"""
    id: str
    name: str
    industry: str = "Manufacturing" # e.g., Bakery, Automotive, Logistics
    nodes: List[str] = Field(default_factory=list) # e.g., ["Line 1", "Dock A"]

class OperationalSignal(BaseModel):
    """A point-in-time observation or telemetry signal"""
    area: str
    signal_type: str # e.g., EQUIPMENT_INSTABILITY, PROCESS_BOTTLENECK
    raw_text: str
    assessor: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ProductionMetric(BaseModel):
    """Standardized output metric for any production line"""
    node_id: str
    planned_units: float
    actual_units: float
    uph_target: float
    uph_actual: float
    status: str = "NORMAL" # NORMAL, DELAY, CRITICAL

class LaborRequirement(BaseModel):
    """Labor needed vs Labor available"""
    node_id: str
    roles_needed: Dict[str, int]
    roles_available: Dict[str, int]
    gap: int
    risk_score: float

class FinancialHealth(BaseModel):
    """Operational ROI and Risk Math"""
    site_id: str
    estimated_revenue_at_risk: float
    labor_efficiency_ratio: float
    recovery_horizon_days: int

class UnifiedFacilityState(BaseModel):
    """The 'Digital Twin' Snapshot of the whole facility"""
    site: SiteInfo
    timestamp: datetime
    production: List[ProductionMetric]
    labor: List[LaborRequirement]
    finance: FinancialHealth
    intelligence_summary: Optional[str] = None
