from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./ticket_analyzer.db"
    processor_kind: str = "ocr"
    poll_interval_seconds: float = 5.0
    batch_size: int = 10
    retry_delay_seconds: float = 30.0
