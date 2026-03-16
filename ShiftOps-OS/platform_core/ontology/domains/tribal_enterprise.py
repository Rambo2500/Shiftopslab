from platform_core.ontology.primitives import Resource, Process, Constraint, Governance

# --- TRIBAL ENTERPRISE DOMAIN ---
# Blends Sovereign Governance with Commercial Operations (e.g., Gaming, Hospitality, Resources)

class TribalGovernance(Governance):
    entity_type: str = "TRIBAL_SOVEREIGN"
    jurisdiction: str = "Tribal Trust Land"
    compliance_frameworks: list = ["NIGC Regulations", "Tribal-State Compact", "Tribal Council Law"]
    revenue_distribution_mandate: bool = True # Must fund community services

def build_gaming_floor_resource(floor_id: str, active_tables: int) -> Resource:
    return Resource(
        id=floor_id,
        name="Table Games Floor",
        category="CAPITAL", # Revenue-generating asset
        capacity=active_tables,
        unit_of_measure="Tables"
    )

def build_compact_constraint(max_machines: int) -> Constraint:
    return Constraint(
        id="state_compact_limit",
        type="REGULATORY",
        description="Maximum Class III gaming machines allowed by State Compact.",
        threshold=max_machines,
        is_hard_stop=True,
        governing_body="Tribal-State Compact"
    )

def build_revenue_process(shift_id: str, tables: Resource, dealers: Resource) -> Process:
    return Process(
        id=f"revenue_gen_{shift_id}",
        name="Gaming Shift Operations",
        inputs=[tables, dealers],
        outputs=[], # Generates financial state, mapped separately
        constraints=[build_compact_constraint(2500)],
        cycle_time_seconds=28800 # 8 hour shift
    )
