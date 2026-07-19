"""
F3: Accessibility Navigator Engine
"""
import json
from backend.gemini_client import GeminiClient
from backend.stadium_data import get_stadium_data

client = GeminiClient()

async def generate_accessible_route(disability_type: str, destination: str, stadium_id: str) -> dict:
    """
    Generates personalized accessible routing and guidance.
    """
    stadium_info = get_stadium_data(stadium_id)
    if not stadium_info:
        return {"status": "error", "response": "Invalid stadium ID."}

    system_prompt = f"""
    You are the FIFA World Cup 2026 Accessibility Navigator.
    You generate personalized turn-by-turn guidance for fans with disabilities at {stadium_info['name']}.
    
    STADIUM KNOWLEDGE BASE:
    {json.dumps(stadium_info['accessibility'])}
    {json.dumps(stadium_info['gates'])}
    
    INSTRUCTIONS:
    1. The fan has requested access for: '{disability_type}'.
    2. The fan's destination is: '{destination}'.
    3. Generate a safe, welcoming, and precise routing guide based on the STADIUM KNOWLEDGE BASE.
    4. Keep the response under 150 words.
    
    SECURITY GUARDRAILS:
    - Never give medical advice.
    - If the destination is unknown, politely direct them to the nearest Guest Services.
    """

    user_prompt = f"I need accessible routing for '{disability_type}' to reach '{destination}'."

    result = await client.generate(
        system_instruction=system_prompt,
        user_prompt=user_prompt
    )
    return result
