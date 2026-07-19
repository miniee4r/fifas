"""
F9: Generative Stadium Modeling Engine
"""
import json
from backend.gemini_client import GeminiClient
from backend.stadium_data import get_stadium_data

client = GeminiClient()

async def generate_stadium_intelligence(seat_section: str, stadium_id: str) -> dict:
    """
    Generates real-time operational intelligence for a specific seat sector.
    Returns structured JSON.
    """
    stadium_info = get_stadium_data(stadium_id)
    if not stadium_info:
        return {"status": "error", "response": "Invalid stadium ID."}

    system_prompt = f"""
    You are the FIFA World Cup 2026 Generative Stadium Assistant.
    You analyze structural stadium data for {stadium_info['name']} and generate real-time operational intelligence for a specific location.
    
    STADIUM TOPOLOGY:
    {json.dumps(stadium_info.get('topology', {}))}
    
    INSTRUCTIONS:
    1. The user has requested intelligence for the following location/seat section: '{seat_section}'.
    2. Generate localized operational intelligence.
    3. You MUST respond in strictly valid JSON format matching this schema:
    {{
        "localized_density": "Prediction of crowd density (e.g. 85% capacity expected)",
        "alternate_route": "Best emergency exit path for this section",
        "safety_announcement": "Multilingual localized announcement script (English and Spanish)",
        "sustainability": "Localized sustainability directive (e.g., Direct waste to Concourse B recycling)"
    }}
    
    SECURITY GUARDRAILS:
    - Output ONLY valid JSON.
    - If the seat section is invalid or unknown, provide a generic safe response in the JSON format.
    """

    user_prompt = f"Location: {seat_section}"

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
