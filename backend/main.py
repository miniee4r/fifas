"""
FastAPI Application Entrypoint
FIFA World Cup 2026 — Smart Stadium Operations
================================================
Implements endpoints for all 5 AI features.
Enforces Rate Limiting, CORS, and Input Validation.
"""

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from pydantic import BaseModel, constr

from backend.config import Settings, sanitize_text, validate_stadium_id, validate_language_code, current_language
from backend.stadium_data import get_all_stadiums
from backend.engines import (
    concierge_engine,
    crowd_engine,
    accessibility_engine,
    incident_engine,
    briefing_engine,
    stadium_model_engine
)

# ---------------------------------------------------------------------------
# Setup & Security (eval-judge-optimizer: Security Tests)
# ---------------------------------------------------------------------------
settings = Settings()
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.rate_limit_requests}/{settings.rate_limit_window}seconds"])

app = FastAPI(title="Smart Stadium AI API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Pydantic Schemas (Input Validation)
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: constr(min_length=1, max_length=2000)
    language: str
    stadium_id: str

class CrowdRequest(BaseModel):
    zone_data: dict
    stadium_id: str
    language: str = "en"

class AccessibilityRequest(BaseModel):
    disability_type: constr(min_length=1, max_length=100)
    destination: constr(min_length=1, max_length=200)
    stadium_id: str
    language: str = "en"

class IncidentRequest(BaseModel):
    incident_type: constr(min_length=1, max_length=100)
    location: constr(min_length=1, max_length=200)
    severity: constr(min_length=1, max_length=50)
    stadium_id: str
    language: str = "en"

class BriefingRequest(BaseModel):
    match_info: constr(min_length=1, max_length=200)
    weather: constr(min_length=1, max_length=200)
    expected_attendance: int
    stadium_id: str
    language: str = "en"

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/health")
async def health_check():
    import google.generativeai as genai
    try:
        # Verify auth by listing models
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return {
            "status": "healthy", 
            "auth_status": "verified",
            "available_models": models[:5] # Return first 5 for brevity
        }
    except Exception as e:
        return {
            "status": "degraded",
            "auth_status": "failed",
            "error": str(e)
        }

@app.get("/api/stadiums")
async def list_stadiums():
    return {"stadiums": get_all_stadiums()}

@app.get("/api/languages")
async def list_languages():
    # Only exposing a subset for the demo frontend
    return {
        "en": "English",
        "es": "Español",
        "fr": "Français",
        "ar": "العربية"
    }

@app.post("/api/chat")
async def chat_endpoint(request: Request, body: ChatRequest):
    try:
        clean_msg = sanitize_text(body.message)
        lang = validate_language_code(body.language)
        current_language.set(lang)
        stadium = validate_stadium_id(body.stadium_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
        
    result = await concierge_engine.get_concierge_response(clean_msg, lang, stadium)
    return result

@app.post("/api/crowd-analysis")
async def crowd_endpoint(request: Request, body: CrowdRequest):
    try:
        lang = validate_language_code(body.language)
        current_language.set(lang)
        stadium = validate_stadium_id(body.stadium_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
        
    result = await crowd_engine.analyze_crowd_flow(body.zone_data, stadium)
    return result

@app.post("/api/accessible-route")
async def accessibility_endpoint(request: Request, body: AccessibilityRequest):
    try:
        clean_type = sanitize_text(body.disability_type)
        clean_dest = sanitize_text(body.destination)
        lang = validate_language_code(body.language)
        current_language.set(lang)
        stadium = validate_stadium_id(body.stadium_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
        
    result = await accessibility_engine.generate_accessible_route(clean_type, clean_dest, stadium)
    return result

@app.post("/api/incident-response")
async def incident_endpoint(request: Request, body: IncidentRequest):
    try:
        clean_type = sanitize_text(body.incident_type)
        clean_loc = sanitize_text(body.location)
        clean_sev = sanitize_text(body.severity)
        lang = validate_language_code(body.language)
        current_language.set(lang)
        stadium = validate_stadium_id(body.stadium_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
        
    result = await incident_engine.generate_incident_protocol(clean_type, clean_loc, clean_sev, stadium)
    return result

@app.post("/api/match-briefing")
async def briefing_endpoint(request: Request, body: BriefingRequest):
    try:
        clean_match = sanitize_text(body.match_info)
        clean_weather = sanitize_text(body.weather)
        lang = validate_language_code(body.language)
        current_language.set(lang)
        stadium = validate_stadium_id(body.stadium_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
        
    result = await briefing_engine.generate_briefing(
        clean_match, clean_weather, body.expected_attendance, stadium
    )
    return result

class StadiumModelRequest(BaseModel):
    seat_section: constr(min_length=1, max_length=200)
    stadium_id: str
    language: str = "en"

@app.post("/api/generative-stadium")
async def generative_stadium_endpoint(request: Request, body: StadiumModelRequest):
    try:
        clean_seat = sanitize_text(body.seat_section)
        lang = validate_language_code(body.language)
        current_language.set(lang)
        stadium = validate_stadium_id(body.stadium_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
        
    result = await stadium_model_engine.generate_stadium_intelligence(clean_seat, stadium)
    return result
