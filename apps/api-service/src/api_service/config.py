from pydantic_settings import BaseSettings, SettingsConfigDict
from persistence.config_utils import get_default_database_url, get_default_storage_path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # These defaults use a root-aware utility to ensure API and Worker share the same folder
    database_url: str = get_default_database_url()
    storage_path: str = get_default_storage_path()
    api_token: str = ""
    poll_interval_seconds: float = 5.0
