import os
import json
import pytest
from app.services.config_service import ConfigService
from pathlib import Path

def test_config_migration_from_llm_to_llm_providers(tmp_path):
    config_file = tmp_path / "agent_config.json"
    
    # Old config format
    old_config = {
        "system_prompt": "Test prompt",
        "llm": {
            "provider": "old_provider",
            "model": "old_model",
            "temperature": 0.5
        },
        "tools_enabled": {},
        "rag": {}
    }
    
    with open(config_file, "w") as f:
        json.dump(old_config, f, indent=2)
    
    # We need to implement migration logic in ConfigService or handle it during loading
    # The instruction says: "Update existing data/agent_config.json ... migrate it"
    # This implies a one-time migration or handling it in the service.
    
    service = ConfigService(config_path=str(config_file))
    config = service.get_config()
    
    # Check if migrated
    assert "llm" not in config
    assert "llm_providers" in config
    assert isinstance(config["llm_providers"], list)
    assert config["llm_providers"][0]["provider"] == "old_provider"
    assert config["llm_providers"][0]["model"] == "old_model"
    assert config["llm_providers"][0]["temperature"] == 0.5

def test_default_config_uses_new_schema(tmp_path):
    config_file = tmp_path / "new_agent_config.json"
    service = ConfigService(config_path=str(config_file))
    config = service.get_config()
    
    assert "llm" not in config
    assert "llm_providers" in config
    assert isinstance(config["llm_providers"], list)
    assert config["llm_providers"][0]["provider"] == "openrouter"
    assert config["llm_providers"][0]["model"] == "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
    assert config["llm_providers"][0]["temperature"] == 0.0
