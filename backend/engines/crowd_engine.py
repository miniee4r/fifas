"""
F2: Crowd Flow Intelligence Engine
"""
import json
from backend.gemini_client import GeminiClient
from backend.stadium_data import get_stadium_data

client = GeminiClient()

async def analyze_crowd_flow(zone_data: dict, stadium_id: str) -> dict:
    """
    Analyzes simulated crowd density data and generates rerouting advisories.
    Returns structured JSON.
    """
    stadium_info = get_stadium_data(stadium_id)
    if not stadium_info:
        return {"status": "error", "response": "Invalid stadium ID."}

    system_prompt = f"""
    You are the FIFA World Cup 2026 Crowd Flow Intelligence AI.
    You analyze real-time density data for {stadium_info['name']} and issue operational commands.
    
    STADIUM KNOWLEDGE BASE:
    {json.dumps(stadium_info)}
    
    INSTRUCTIONS:
    1. Analyze the provided current zone density data.
    2. Identify any bottlenecks (zones > 85% capacity).
    3. Generate rerouting commands to redirect fans to under-utilized gates/zones.
    4. You MUST respond in strictly valid JSON format matching this schema:
    {{
        "bottlenecks_detected": ["Zone1", "Zone2"],
        "severity_level": "LOW|MEDIUM|HIGH|CRITICAL",
        "rerouting_commands": ["Open Gate X", "Direct fans from Y to Z"],
        "staff_advisory": "Brief advice for stewards"
    }}
    
    SECURITY GUARDRAILS:
    - Output ONLY valid JSON. No markdown formatting, no code blocks, no conversational text.
    """

    user_prompt = json.dumps(zone_data)

    result = await client.generate(
        system_instruction=system_prompt,
        user_prompt=user_prompt,
        response_mime_type="application/json"
    )
    
    if result["status"] == "success":
        try:
            # Parse it to ensure it's valid JSON before returning
            parsed = json.loads(result["response"])
            return {"status": "success", "data": parsed}
        except json.JSONDecodeError:
            return {"status": "error", "response": "AI returned invalid JSON."}
            
    return result
