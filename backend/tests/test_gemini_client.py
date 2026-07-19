import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from backend.gemini_client import GeminiClient

@pytest.fixture
def client():
    return GeminiClient()

@pytest.mark.asyncio
async def test_generate_success(client, mocker):
    mock = mocker.patch("asyncio.to_thread", new_callable=AsyncMock)
    class MockResponse:
        text = "Mocked API Response"
    mock.return_value = MockResponse()
    
    res = await client.generate("system", "user")
    assert res["status"] == "success"
    assert res["response"] == "Mocked API Response"

@pytest.mark.asyncio
async def test_generate_token_overflow(client):
    # Enforces efficiency / security rules by preventing massive payloads
    long_prompt = "word " * 5000
    res = await client.generate("system", long_prompt)
    assert res["status"] == "error"
    assert "too large" in res["response"].lower()

@pytest.mark.asyncio
async def test_generate_timeout_fallback(client, mocker):
    # Mocks a timeout exception on asyncio.wait_for
    mock = mocker.patch("asyncio.wait_for", new_callable=AsyncMock)
    mock.side_effect = asyncio.TimeoutError()
    
    # We patch sleep to avoid actually waiting during test execution
    mocker.patch("asyncio.sleep", new_callable=AsyncMock)
    
    res = await client.generate("system", "user")
    assert res["status"] == "fallback"
    assert "timed out" in res["response"]

@pytest.mark.asyncio
async def test_generate_general_error_fallback(client, mocker):
    mock = mocker.patch("asyncio.wait_for", new_callable=AsyncMock)
    mock.side_effect = Exception("Google API Down")
    mocker.patch("asyncio.sleep", new_callable=AsyncMock)
    
    res = await client.generate("system", "user")
    assert res["status"] == "fallback"
    assert "unavailable" in res["response"]
