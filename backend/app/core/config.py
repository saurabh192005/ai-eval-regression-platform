from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Eval Platform"
    database_url: str = "postgresql://postgres:pass@localhost:5432/postgres"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()