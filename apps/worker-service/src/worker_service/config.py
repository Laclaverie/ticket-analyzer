from pydantic_settings import BaseSettings, SettingsConfigDict
from persistence.config_utils import get_default_database_url

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # These defaults use a root-aware utility to ensure API and Worker share the same folder
    database_url: str = get_default_database_url()
    processor_kind: str = "ocr"
    tesseract_cmd: str | None = None
    debug_preprocessor: bool = True
    poll_interval_seconds: float = 5.0
    batch_size: int = 10
    retry_delay_seconds: float = 30.0

    # YOLO detection settings
    yolo_enabled: bool = True
    use_yolo_pipeline: bool = True  # If True, uses YOLO as the ONLY segmentation step
    yolo_model_path: str = "data/weights/best.pt"
    yolo_confidence: float = 0.55
