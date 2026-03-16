import json
import uuid
from datetime import datetime
from platform_core.ontology.loader import OntologyLoader
from platform_core.ontology.logic import ConstraintParser, StateResolver
from platform_core.kernel.trace import ControlTrace

def run_demo():
    print("🚀 IGNITING SHIFTOPS-OS KERNEL...")
    
    # 1. Initialize Loader
    loader = OntologyLoader()
    
    # 2. Load the 'Wildcard' (Satellite Pack)
    print("\n[Phase 1] Loading Ontology Module: satellite_ops_v1")
    pack = loader.get_pack("satellite_ops_v1")
    
    # 3. Ingest Raw Telemetry (Simulated Reality)
    # We are simulating a satellite that has dropped below its safety floor (290km vs 300km limit)
    telemetry = {
        "raw_altitude": 290.5,
        "battery_charge": 94.2,
        "sensor_7_value": 42.0 # Mapped to thermal_index
    }
    print(f"[Phase 2] Ingesting Telemetry: Altitude={telemetry['raw_altitude']}km")

    # 4. State Resolution (Spreadsheet Recalc)
    resolved_values = StateResolver.resolve_snapshot(pack, telemetry)
    
    # 5. Constraint Evaluation (The Judge)
    violations = []
    for constraint in pack.constraints:
        passed = ConstraintParser.evaluate(constraint.expression, resolved_values)
        if not passed:
            violations.append({
                "id": constraint.id,
                "expression": constraint.expression,
                "message": constraint.error_message,
                "offending_value": resolved_values.get(constraint.expression.split()[0])
            })

    # 6. Generate the Universal Trace
    trace = ControlTrace(
        trace_id=str(uuid.uuid4()),
        actor="System_Autonomic_Guard",
        intent={"action": "MAINTAIN_ORBIT", "entity_id": "SAT-01"},
        ontology_id=pack.ontology_id,
        snapshot=resolved_values,
        violations=violations,
        status="BLOCK" if violations else "PASS"
    )

    # 7. OUTPUT THE RESULT
    print("\n" + "="*40)
    print(" UNIVERSAL CONTROL TRACE (Audit Log)")
    print("="*40)
    print(trace.to_human_narrative())
    print("="*40)
    
    if trace.status == "BLOCK":
        print("\nACTION: Intent Blocked. Actuator 'thruster_control_api' locked.")
        print("REASON: Orbital decay safety threshold violated.")
    else:
        print("\nACTION: Intent Authorized. Transition committed.")

if __name__ == "__main__":
    run_demo()
