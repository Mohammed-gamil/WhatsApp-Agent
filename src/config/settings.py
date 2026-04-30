from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "WhatsApp AI Agent"
    whats360_api_url: str = "https://apis.whats360.live"
    whats360_token: str = ""
    whats360_instance_id: str = ""
    openai_api_key: str = ""
    groq_api_key: str = ""
    openrouter_api_key: str = ""
    
    active_llm_provider: str = "openrouter"
    meta_verify_token: str = "test_token"
    meta_access_token: str = "test_access"
    database_url: str = "postgresql+psycopg://user:pass@localhost:5432/db"
    
    # Comma-separated list of phone numbers authorized to use /set-model
    admin_numbers: str = "" 

    @property
    def admin_numbers_list(self) -> List[str]:
        return [num.strip() for num in self.admin_numbers.split(",") if num.strip()]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

def get_settings() -> Settings:
    return Settings()
