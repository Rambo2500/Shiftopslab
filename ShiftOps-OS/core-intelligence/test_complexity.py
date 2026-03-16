import json
from intent_to_code.support.architecture_engine import ArchitectureEngine

engine = ArchitectureEngine()
prompt = "i need a excel spread sheet build that will track employee punches using a qr code like system that can track into excel"

print("Running synthesis for LOW complexity request...")
snapshot = engine.generate_snapshot(
    goal="QR Punch Tracker",
    user_request=prompt
)

print(f"\nSynthesis complete!")
print(f"Complexity: {snapshot['diagnostics'].get('complexity')}")
print(f"Domain Archetype: {snapshot['domain_archetype']}")

# Check if process flow is in the manifest
manifest = snapshot.get("surface_manifest", {})
surfaces = manifest.get("surfaces", [])
flow_surface = next((s for s in surfaces if s['id'] == 'process_flow'), None)

if flow_surface:
    print("\n[SUCCESS] Process Flow projection found in manifest.")
    print(f"Flow Layers: {len(flow_surface.get('layers', []))}")
else:
    print("\n[FAILURE] Process Flow projection NOT found.")

# Save the snapshot
with open("qr_punch_snapshot.json", "w") as f:
    json.dump(snapshot, f, indent=2)
print("\nSnapshot saved to qr_punch_snapshot.json")
