import os
import json
import pytest
from app.services.config_service import ConfigService

def test_get_config_returns_default():
    service = ConfigService()
    config = service.get_config()
    assert config["llm"]["provider"] == "openrouter"
    assert config["tools_enabled"]["send_whatsapp_text"] is True

def test_update_config_persists_changes(tmp_path):
    config_file = tmp_path / "test_config.json"
    service = ConfigService(config_path=str(config_file))
    
    new_config = service.get_config()
    new_config["llm"]["temperature"] = 0.5
    
    service.update_config(new_config)
    
    # Reload and verify
    updated_config = service.get_config()
    assert updated_config["llm"]["temperature"] == 0.5
