import json
from intent_to_code.support.architecture_engine import ArchitectureEngine

engine = ArchitectureEngine()
prompt = """
Design an operational platform for coordinating emergency wildfire response across three U.S. states simultaneously. The system must ingest:
• live satellite imagery
• drone telemetry streams
• firefighter GPS positions
• weather forecasts
• road closure data
• hospital capacity data
• emergency call center feeds
The platform must provide three different operational surfaces:
A command center dashboard for state emergency operations centers showing:
real-time incident severity ranking
predicted fire spread zones
available firefighting resources
evacuation progress
A mobile responder interface for firefighters showing:
assigned tasks
navigation routes avoiding blocked roads
nearby hazards and fire fronts
live updates from command
An executive briefing surface that summarizes:
casualty counts
property damage estimates
evacuation status by county
resource utilization
System constraints:
• Must process 1 million telemetry events per minute
• Must remain operational during regional network outages
• Must support simulation of evacuation scenarios
• Must automatically recommend resource deployment
"""

print("Running synthesis...")
snapshot = engine.generate_snapshot("wildfire_response", prompt)
with open("wildfire_snapshot.json", "w") as f:
    json.dump(snapshot, f, indent=2)

print("Synthesis complete!")
print(f"Confidence: {snapshot['diagnostics']['confidence']}")
print(f"Fitness Score: {snapshot['diagnostics']['fitness_score']}")

# Print out a sample of the generated code to show the new endpoints
found_endpoints = False
for filepath, content in snapshot['repo'].items():
    if "main.py" in filepath and "def handle_" in content:
        found_endpoints = True
        print(f"\n--- {filepath} ---")
        # Print just the endpoint definitions
        lines = content.split('\n')
        for line in lines:
            if line.startswith("@app.") or line.startswith("async def"):
                print(line)

if not found_endpoints:
    print("\nNo specific UI-bound endpoints were found. Let's check the surface manifest bindings:")
    print(json.dumps(snapshot.get("surface_manifest", {}), indent=2)[:500] + "...")
