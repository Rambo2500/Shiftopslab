import sys
import json
from intent_to_code.models.gemini_adapter import GeminiAdapter

def main():
    if len(sys.argv) < 2:
        print("Usage: python draft.py 'Your natural language request'")
        sys.exit(1)

    request = sys.argv[1]
    drafter = GeminiAdapter()
    intent = drafter.draft_intent(request)

    output_path = "examples/intent/drafted_intent.json"
    with open(output_path, "w") as f:
        json.dump(intent, f, indent=2)

    print(f"Intent drafted successfully to: {output_path}")

if __name__ == "__main__":
    main()
