import logging
import sys
import os

from persistence.base import Base
from persistence.engine import create_db_engine, create_session_factory
import persistence.models  # noqa: F401

from worker_service.config import Settings
from worker_service.poller import JobPoller
from worker_service.processor_factory import create_processor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)


def main() -> None:
    settings = Settings()

    # Log absolute database path for debugging
    db_path = settings.database_url
    if db_path.startswith("sqlite:///"):
        # Handle relative vs absolute sqlite paths
        raw_path = db_path.replace("sqlite:///", "")
        abs_path = os.path.abspath(raw_path)
        logger.info("Connecting to SQLite database at: %s", abs_path)
    else:
        logger.info("Connecting to database: %s", db_path)

    engine = create_db_engine(settings.database_url)
    Base.metadata.create_all(engine)

    factory = create_session_factory(engine)
    db = factory()

    processor = create_processor(db, settings.processor_kind)
    poller = JobPoller(
        db,
        processor,
        poll_interval_seconds=settings.poll_interval_seconds,
        batch_size=settings.batch_size,
        retry_delay_seconds=settings.retry_delay_seconds,
    )

    logger.info("Starting worker service with processor=%s", processor.name)
    poller.run()


if __name__ == "__main__":
    main()
