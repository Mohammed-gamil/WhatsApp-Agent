from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Whats360 Configuration
    whats360_token: str = ""
    whats360_instance_id: str = ""
    whats360_base_url: str = ""

    # AI Configuration
    openai_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    llm_model: str = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
    
    # App Configuration
    app_name: str = "WhatsApp AI Agent"
    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
