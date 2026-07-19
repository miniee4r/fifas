import pytest

def test_health_endpoint(api_client):
    response = api_client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_stadiums_endpoint(api_client):
    response = api_client.get("/api/stadiums")
    assert response.status_code == 200
    assert "stadiums" in response.json()
    assert len(response.json()["stadiums"]) > 0

def test_languages_endpoint(api_client):
    response = api_client.get("/api/languages")
    assert response.status_code == 200
    assert "en" in response.json()

def test_chat_endpoint_success(api_client, mock_gemini_generate):
    response = api_client.post("/api/chat", json={
        "message": "Hello",
        "language": "en",
        "stadium_id": "metlife"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_chat_endpoint_validation_error(api_client):
    # Missing required field
    response = api_client.post("/api/chat", json={
        "message": "Hello"
    })
    assert response.status_code == 422

def test_chat_endpoint_security_xss(api_client, mock_gemini_generate):
    # Ensures payload reaches the engine sanitized
    response = api_client.post("/api/chat", json={
        "message": "<script>alert(1)</script>",
        "language": "en",
        "stadium_id": "metlife"
    })
    assert response.status_code == 200
    call_kwargs = mock_gemini_generate.call_args.kwargs
    assert "&lt;script&gt;" in call_kwargs["user_prompt"]

def test_crowd_endpoint_success(api_client, mock_gemini_generate):
    mock_gemini_generate.return_value = {
        "status": "success",
        "response": '{"severity_level": "LOW", "bottlenecks_detected": []}'
    }
    response = api_client.post("/api/crowd-analysis", json={
        "zone_data": {"North": 40},
        "stadium_id": "metlife"
    })
    assert response.status_code == 200
    assert response.json()["data"]["severity_level"] == "LOW"

def test_stadium_model_endpoint_success(api_client, mock_gemini_generate):
    mock_gemini_generate.return_value = {
        "status": "success",
        "response": '{"localized_density": "80%", "alternate_route": "Gate B", "safety_announcement": "Attention", "sustainability": "Recycle"}'
    }
    response = api_client.post("/api/generative-stadium", json={
        "seat_section": "Block 101",
        "stadium_id": "metlife"
    })
    assert response.status_code == 200
    assert response.json()["data"]["alternate_route"] == "Gate B"

def test_cors_headers(api_client):
    # Test that CORS middleware is applied
    response = api_client.options("/api/chat", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST"
    })
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

def test_rate_limiting(api_client):
    # Simulate spamming the health endpoint to hit the rate limit
    # Config default is 60/min
    for _ in range(65):
        resp = api_client.get("/api/health")
        if resp.status_code == 429:
            assert "Retry-After" in resp.headers
            return
    pytest.fail("Rate limit was not enforced")
