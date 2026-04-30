import json
import os
from pathlib import Path
from loguru import logger

class ConfigService:
    def __init__(self, config_path: str = "data/agent_config.json"):
        self.config_path = Path(config_path)
        self._ensure_config_exists()

    def _ensure_config_exists(self):
        if not self.config_path.parent.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.config_path.exists():
            default_config = {
                "system_prompt": "You are a professional WhatsApp AI Assistant. You MUST ALWAYS use the 'send_whatsapp_text' tool to send your reply to the user. Never just type a message in plain text; if you do, the user will never see it.",
                "llm": {
                    "provider": "openrouter",
                    "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
                    "temperature": 0.0
                },
                "tools_enabled": {
                    "send_whatsapp_text": True,
                    "send_whatsapp_image": True,
                    "send_whatsapp_document": True,
                    "launch_whatsapp_campaign": True
                },
                "rag": {
                    "enabled": False,
                    "backend_url": ""
                }
            }
            with open(self.config_path, "w") as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default config at {self.config_path}")

    def get_config(self) -> dict:
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading config: {e}")
            return {}

    def update_config(self, new_config: dict):
        try:
            with open(self.config_path, "w") as f:
                json.dump(new_config, f, indent=2)
            logger.info("Configuration updated successfully")
        except Exception as e:
            logger.error(f"Error updating config: {e}")
            raise
