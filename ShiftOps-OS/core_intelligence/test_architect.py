import json
from pathlib import Path
from intent_to_code.support.architecture_engine import ArchitectureEngine

def test_prompts():
    engine = ArchitectureEngine()
    prompts = [
        ("3PL Fulfillment Network", "Design a 3PL fulfillment network supporting e-commerce shipping."),
        ("Rural Emergency Dispatch", "Design a rural emergency dispatch coordination platform."),
        ("Regional ISP Monitoring", "Design a regional ISP network monitoring system."),
        ("EMS Production V1", "Design a production-grade Rural Emergency Dispatch platform. Focus on real-time unit tracking and automated logic.")
    ]

    for goal, request in prompts:
        print(f"\n--- Architecting: {goal} ---")
        try:
            # We use run_full_cycle to generate the blueprint and components
            base_dir = Path("build") / goal.replace(" ", "_")
            result = engine.run_full_cycle(goal, request, base_dir=base_dir)
            
            print(f"Goal: {result['goal']}")
            print(f"Fitness Score: {result['evaluation']['total_score']:.2f}")
            print(f"Components: {len(result['system_intent']['outputs']['system']['components'])}")
            print(f"Blueprint saved to: {base_dir / 'architecture_blueprint.json'}")
            
        except Exception as e:
            print(f"Error architecting {goal}: {str(e)}")

if __name__ == "__main__":
    test_prompts()
