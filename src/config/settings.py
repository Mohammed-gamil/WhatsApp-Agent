from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "WhatsApp Sales Agent"
    active_llm_provider: str = "openai"
    meta_verify_token: str = "test_token"
    meta_access_token: str = "test_access"
    database_url: str = "postgresql://user:pass@localhost:5432/db"

def get_settings() -> Settings:
    return Settings()
