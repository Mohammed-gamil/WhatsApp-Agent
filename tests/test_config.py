# tests/test_config.py
import pytest
from src.config.settings import Settings, get_settings

def test_settings_load_defaults():
    settings = get_settings()
    assert settings.app_name == "WhatsApp Sales Agent"
    assert settings.active_llm_provider == "openai"
