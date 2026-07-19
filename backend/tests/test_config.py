import pytest
from backend.config import sanitize_text, validate_stadium_id, validate_language_code, Settings

def test_sanitize_text_normal():
    assert sanitize_text("  hello world  ") == "hello world"

def test_sanitize_text_xss():
    # Escapes HTML to prevent XSS
    raw = "<script>alert(1)</script>"
    clean = sanitize_text(raw)
    assert clean == "&lt;script&gt;alert(1)&lt;/script&gt;"

def test_sanitize_text_null_bytes():
    with pytest.raises(ValueError, match="null bytes"):
        sanitize_text("bad\x00data")

def test_sanitize_text_length():
    with pytest.raises(ValueError, match="exceeds maximum length"):
        sanitize_text("A" * 2001)

def test_sanitize_text_empty():
    with pytest.raises(ValueError, match="must not be empty"):
        sanitize_text("   ")

def test_validate_stadium_id():
    assert validate_stadium_id("metlife") == "metlife"
    assert validate_stadium_id("azteca-123") == "azteca-123"
    
    with pytest.raises(ValueError, match="Invalid stadium ID"):
        validate_stadium_id("invalid!id")

def test_validate_language_code():
    assert validate_language_code("EN") == "en"
    
    with pytest.raises(ValueError, match="Unsupported language"):
        validate_language_code("xx")

def test_settings_load_successfully():
    s = Settings()
    assert s.genai_api_key == "mock_key_for_tests"
    assert "http://localhost:3000" in s.cors_origins
