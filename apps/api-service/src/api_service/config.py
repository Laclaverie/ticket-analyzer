from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./data/ticket_analyzer.db"
    storage_path: str = "./data/images"
    api_token: str = ""
    poll_interval_seconds: float = 5.0
