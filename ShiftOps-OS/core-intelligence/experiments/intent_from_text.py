import json
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Foundry project endpoint
FOUNDRY_ENDPOINT = "https://shiftops-kernel-resource.services.ai.azure.com/api/projects/shiftops-kernel"

# Single agent whose ONLY job is intent translation
AGENT_NAME = "intent-translator"

def extract_intent(text: str) -> dict:
    """
    Translate messy human input into structured intent JSON.

    Responsibilities:
    - Call Foundry exactly once
    - Return JSON that matches intent_schema.json
    - Do NOT invent missing values
    - Do NOT generate code
    """

    project_client = AIProjectClient(
        endpoint=FOUNDRY_ENDPOINT,
        credential=DefaultAzureCredential(),
    )

    agent = project_client.agents.get(agent_name=AGENT_NAME)
    openai_client = project_client.get_openai_client()

    system_prompt = """
You translate human requests into STRICT JSON that conforms to this schema:

{
  "goal": "string",
  "inputs": ["string"],
  "constraints": ["string"],
  "confidence": "LOW | MEDIUM | HIGH"
}

Rules:
- Output JSON ONLY.
- Do NOT generate code.
- Do NOT invent values.
- If information is missing, leave arrays empty and set confidence to LOW.
"""

    
    response = openai_client.responses.create(
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )

    return json.loads(response.output_text)

