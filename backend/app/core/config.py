from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Eval Platform"
    database_url: str = "postgresql+psycopg://postgres:pass@localhost:5432/evaldb"
    model_config = SettingsConfigDict(env_file=".env")
    groq_api_key: str = ""
    groq_base_url: str = "https://api.groq.com/openai/v1"


settings = Settings()