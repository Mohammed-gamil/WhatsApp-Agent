# tests/test_config.py
import pytest
from src.config.settings import Settings, get_settings

def test_settings_load_defaults():
    settings = get_settings()
    assert settings.app_name == "WhatsApp AI Agent"
    assert settings.whats360_api_url == "https://apis.whats360.live"
    # These are loaded from .env
    assert settings.whats360_token != ""
    assert settings.active_llm_provider == "openrouter"
