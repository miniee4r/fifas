"""
F6: Incident Response Advisor
"""
import json
from backend.gemini_client import GeminiClient
from backend.stadium_data import get_stadium_data

client = GeminiClient()

async def generate_incident_protocol(incident_type: str, location: str, severity: str, stadium_id: str) -> dict:
    """
    Generates prioritized operational action plans for stadium incidents.
    Returns structured JSON.
    """
    stadium_info = get_stadium_data(stadium_id)
    if not stadium_info:
        return {"status": "error", "response": "Invalid stadium ID."}

    system_prompt = f"""
    You are the FIFA World Cup 2026 Incident Response Advisor.
    You generate strict, prioritized operational protocols for incidents at {stadium_info['name']}.
    
    STADIUM KNOWLEDGE BASE:
    {json.dumps(stadium_info)}
    
    INSTRUCTIONS:
    1. Analyze the incident: Type={incident_type}, Location={location}, Severity={severity}.
    2. Generate a 3-step action protocol for operations staff.
    3. You MUST respond in strictly valid JSON format matching this schema:
    {{
        "incident_classification": "Brief classification",
        "priority_level": "P1|P2|P3",
        "action_protocol": ["Step 1", "Step 2", "Step 3"],
        "required_personnel": ["Medics", "Security", etc]
    }}
    
    SECURITY GUARDRAILS:
    - Output ONLY valid JSON.
    - Never suggest actions that would induce panic (e.g. "evacuate immediately" unless severity is extreme).
    """

    user_prompt = f"Incident Report: {incident_type} at {location}. Reported severity: {severity}."

    result = await client.generate(
        system_instruction=system_prompt,
        user_prompt=user_prompt,
        response_mime_type="application/json"
    )
    
    if result["status"] == "success":
        try:
            parsed = json.loads(result["response"])
            return {"status": "success", "data": parsed}
        except json.JSONDecodeError:
            return {"status": "error", "response": "AI returned invalid JSON."}
            
    return result
