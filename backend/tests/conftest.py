import pytest
import os
from unittest.mock import AsyncMock

# Must set before any modules load to avoid fail-fast in config.py
os.environ["GENAI_API_KEY"] = "mock_key_for_tests"
os.environ["CORS_ORIGINS"] = "http://localhost:3000"

from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture
def api_client():
    """Provides a TestClient for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def mock_gemini_generate(mocker):
    """
    Mocks the GeminiClient.generate method universally across all tests.
    Returns a successful response by default.
    """
    mock = mocker.patch("backend.gemini_client.GeminiClient.generate", new_callable=AsyncMock)
    mock.return_value = {
        "status": "success",
        "response": "Mocked AI response"
    }
    return mock
