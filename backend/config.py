"""
Configuration & Security Scaffolding
FIFA World Cup 2026 — Smart Stadium Operations
================================================
Handles: Environment loading, input validation, rate limiting config,
and security constants. Zero hardcoded secrets.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List
import contextvars

current_language = contextvars.ContextVar("current_language", default="en")

# ---------------------------------------------------------------------------
# Safe environment loading — .env file is read ONLY from project root
# ---------------------------------------------------------------------------
from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)


def _require_env(key: str) -> str:
    """Fail fast if a required environment variable is missing."""
    value = os.getenv(key)
    if not value or value.strip() == "" or value == "your_api_key_here":
        raise EnvironmentError(
            f"Missing or placeholder value for required env var: {key}. "
            f"Please set it in your .env file."
        )
    return value.strip()


# ---------------------------------------------------------------------------
# Application Settings (dataclass for type safety & immutability)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Settings:
    """Immutable application settings loaded from environment variables."""

    # GenAI
    genai_api_key: str = field(default_factory=lambda: _require_env("GENAI_API_KEY"))

    # Server
    api_host: str = field(
        default_factory=lambda: os.getenv("API_HOST", "0.0.0.0")
    )
    api_port: int = field(
        default_factory=lambda: int(os.getenv("API_PORT", "8000"))
    )
    api_env: str = field(
        default_factory=lambda: os.getenv("API_ENV", "development")
    )

    # Rate Limiting
    rate_limit_requests: int = field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
    )
    rate_limit_window: int = field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    )

    # CORS
    cors_origins: List[str] = field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS", "http://localhost:3000"
            ).split(",")
        ]
    )


# ---------------------------------------------------------------------------
# Input Validation & Sanitization Utilities
# ---------------------------------------------------------------------------
import re
import html


def sanitize_text(raw: str, max_length: int = 2000) -> str:
    """
    Sanitize user-provided text input.
    - Strips leading/trailing whitespace
    - Escapes HTML entities (prevents XSS)
    - Enforces max length
    - Rejects null bytes and control characters
    """
    if not isinstance(raw, str):
        raise ValueError("Input must be a string.")
    # Reject null bytes
    if "\x00" in raw:
        raise ValueError("Input contains null bytes.")
    # Strip and enforce length
    cleaned = raw.strip()
    if len(cleaned) == 0:
        raise ValueError("Input must not be empty.")
    if len(cleaned) > max_length:
        raise ValueError(f"Input exceeds maximum length of {max_length} characters.")
    # Remove control characters (except newline/tab)
    cleaned = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]', '', cleaned)
    # Escape HTML entities
    cleaned = html.escape(cleaned, quote=True)
    return cleaned


def validate_stadium_id(stadium_id: str) -> str:
    """Validate stadium identifiers — alphanumeric + hyphens only."""
    if not isinstance(stadium_id, str):
        raise ValueError("Stadium ID must be a string.")
    pattern = r'^[a-zA-Z0-9\-]{1,50}$'
    if not re.match(pattern, stadium_id):
        raise ValueError(
            "Invalid stadium ID. Must be 1-50 alphanumeric characters or hyphens."
        )
    return stadium_id


def validate_language_code(code: str) -> str:
    """Validate ISO 639-1 language codes."""
    valid_codes = {
        "en", "es", "fr", "ar", "pt", "de", "it", "ja", "ko", "zh",
        "hi", "ru", "nl", "sv", "no", "da", "fi", "pl", "tr", "th",
    }
    if code.lower() not in valid_codes:
        raise ValueError(f"Unsupported language code: {code}")
    return code.lower()


# ---------------------------------------------------------------------------
# Security Constants
# ---------------------------------------------------------------------------
MAX_PROMPT_TOKENS = 4096
ALLOWED_CONTENT_TYPES = {"application/json"}
REQUEST_TIMEOUT_SECONDS = 30
