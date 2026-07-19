"""
F8: Match-Day Briefing Generator
"""
import json
from backend.gemini_client import GeminiClient
from backend.stadium_data import get_stadium_data

client = GeminiClient()

async def generate_briefing(match_info: str, weather: str, expected_attendance: int, stadium_id: str) -> dict:
    """
    Generates comprehensive pre-match ops briefings.
    Returns structured JSON.
    """
    stadium_info = get_stadium_data(stadium_id)
    if not stadium_info:
        return {"status": "error", "response": "Invalid stadium ID."}

    system_prompt = f"""
    You are the FIFA World Cup 2026 Operations Briefing Generator.
    You generate pre-match briefings for {stadium_info['name']}.
    Capacity: {stadium_info['capacity']}
    
    INSTRUCTIONS:
    1. Analyze the inputs: Match={match_info}, Weather={weather}, Expected Attendance={expected_attendance}.
    2. Calculate attendance percentage and highlight any weather risks.
    3. You MUST respond in strictly valid JSON format matching this schema:
    {{
        "executive_summary": "1 sentence overview",
        "attendance_outlook": "Analysis of crowd size vs capacity",
        "weather_impact": "Operational impacts of the weather",
        "key_focus_areas": ["Focus 1", "Focus 2"]
    }}
    
    SECURITY GUARDRAILS:
    - Output ONLY valid JSON.
    """

    user_prompt = f"Match: {match_info}. Weather: {weather}. Expected Attendance: {expected_attendance}."

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
