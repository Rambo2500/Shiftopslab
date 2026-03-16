from platform_core.ontology.primitives import Resource, Process, Constraint, Governance

# --- CORRECTIONS & INSTITUTIONAL DOMAIN ---

class CorrectionsGovernance(Governance):
    entity_type: str = "STATE_OR_FEDERAL_AGENCY"
    compliance_frameworks: list = ["BOP Standards", "Eighth Amendment Mandates", "State Security Protocols"]

def build_cell_block_resource(block_id: str, capacity: int) -> Resource:
    return Resource(
        id=block_id,
        name=f"Cell Block {block_id}",
        category="LAND", # Spatial capacity
        capacity=capacity,
        unit_of_measure="Beds"
    )

def build_guard_resource(shift_id: str, headcount: int) -> Resource:
    return Resource(
        id=f"guards_{shift_id}",
        name="Security Personnel",
        category="LABOR",
        capacity=headcount,
        unit_of_measure="Officers"
    )

def build_security_constraint(ratio_required: float) -> Constraint:
    return Constraint(
        id="inmate_to_guard_ratio",
        type="SAFETY",
        description="Maximum allowed inmates per guard on floor.",
        threshold=ratio_required,
        is_hard_stop=True,
        governing_body="Department of Corrections"
    )

def build_movement_process(movement_id: str, guards: Resource, time_limit_sec: float) -> Process:
    return Process(
        id=movement_id,
        name="Mass Movement (Yard to Block)",
        inputs=[guards],
        outputs=[], # The output is state change, not a new resource
        constraints=[build_security_constraint(50.0)],
        cycle_time_seconds=time_limit_sec
    )
