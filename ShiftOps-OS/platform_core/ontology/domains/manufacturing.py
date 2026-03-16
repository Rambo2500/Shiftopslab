from platform_core.ontology.primitives import Resource, Process, Constraint, Governance

# --- MANUFACTURING & LOGISTICS DOMAIN (e.g., Elkhart Bakery) ---

class CommercialGovernance(Governance):
    entity_type: str = "CORPORATE"
    jurisdiction: str = "Commercial Sector"
    compliance_frameworks: list = ["OSHA", "FDA/FSMA", "Corporate Quality Standards"]

def build_production_line(line_id: str, uph: float) -> Resource:
    return Resource(
        id=line_id,
        name=f"Production Line {line_id}",
        category="CAPITAL",
        capacity=uph,
        unit_of_measure="Units/Hour"
    )

def build_delivery_constraint(deadline_epoch: float) -> Constraint:
    return Constraint(
        id="drop_dead_window",
        type="TIME_WINDOW",
        description="The latest time a load can leave the dock without failing the SLA.",
        threshold=deadline_epoch,
        is_hard_stop=True,
        governing_body="Customer SLA"
    )

def build_fulfillment_process(order_id: str, line: Resource, labor: Resource) -> Process:
    return Process(
        id=f"fulfill_{order_id}",
        name="Order Fulfillment",
        inputs=[line, labor],
        outputs=[], # Outputs finished goods inventory
        constraints=[], # Handled dynamically
        cycle_time_seconds=3600
    )
