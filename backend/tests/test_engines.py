import pytest
from backend.engines.concierge_engine import get_concierge_response
from backend.engines.crowd_engine import analyze_crowd_flow
from backend.engines.accessibility_engine import generate_accessible_route
from backend.engines.incident_engine import generate_incident_protocol
from backend.engines.briefing_engine import generate_briefing

# ---------------------------------------------------------
# F1: Concierge
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_concierge_success(mock_gemini_generate):
    res = await get_concierge_response("Where is the food?", "en", "metlife")
    assert res["status"] == "success"
    # Ensure stadium context injection happened
    call_kwargs = mock_gemini_generate.call_args.kwargs
    assert "MetLife Stadium" in call_kwargs["system_instruction"]
    assert "en" in call_kwargs["system_instruction"]

@pytest.mark.asyncio
async def test_concierge_invalid_stadium(mock_gemini_generate):
    res = await get_concierge_response("Where is the food?", "en", "invalid")
    assert res["status"] == "error"

# ---------------------------------------------------------
# F2: Crowd Flow
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_crowd_success(mock_gemini_generate):
    # Mocking the JSON response from Gemini
    mock_gemini_generate.return_value = {
        "status": "success",
        "response": '{"severity_level": "HIGH", "bottlenecks_detected": ["South"]}'
    }
    zone_data = {"North": 40, "South": 95}
    res = await analyze_crowd_flow(zone_data, "metlife")
    assert res["status"] == "success"
    assert res["data"]["severity_level"] == "HIGH"

@pytest.mark.asyncio
async def test_crowd_invalid_json(mock_gemini_generate):
    mock_gemini_generate.return_value = {
        "status": "success",
        "response": "I am an AI, I cannot output JSON."
    }
    res = await analyze_crowd_flow({"North": 40}, "metlife")
    assert res["status"] == "error"
    assert "invalid JSON" in res["response"]

# ---------------------------------------------------------
# F3: Accessibility
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_accessibility_success(mock_gemini_generate):
    res = await generate_accessible_route("wheelchair", "Section 104", "metlife")
    assert res["status"] == "success"
    call_kwargs = mock_gemini_generate.call_args.kwargs
    assert "wheelchair" in call_kwargs["user_prompt"]

# ---------------------------------------------------------
# F6: Incident Response
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_incident_success(mock_gemini_generate):
    mock_gemini_generate.return_value = {
        "status": "success",
        "response": '{"priority_level": "P1", "action_protocol": ["Deploy Medics"]}'
    }
    res = await generate_incident_protocol("medical", "Gate 4", "High", "metlife")
    assert res["status"] == "success"
    assert res["data"]["priority_level"] == "P1"

# ---------------------------------------------------------
# F8: Briefing
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_briefing_success(mock_gemini_generate):
    mock_gemini_generate.return_value = {
        "status": "success",
        "response": '{"executive_summary": "All good", "weather_impact": "None"}'
    }
    res = await generate_briefing("USA vs MEX", "Sunny", 80000, "metlife")
    assert res["status"] == "success"
    assert "All good" in res["data"]["executive_summary"]

# ---------------------------------------------------------
# F9: Generative Stadium Assistant
# ---------------------------------------------------------
from backend.engines.stadium_model_engine import generate_stadium_intelligence

@pytest.mark.asyncio
async def test_stadium_model_success(mock_gemini_generate):
    mock_gemini_generate.return_value = {
        "status": "success",
        "response": '{"localized_density": "80%", "alternate_route": "Gate B", "safety_announcement": "Attention", "sustainability": "Recycle"}'
    }
    res = await generate_stadium_intelligence("Block 101", "metlife")
    assert res["status"] == "success"
    assert res["data"]["alternate_route"] == "Gate B"
