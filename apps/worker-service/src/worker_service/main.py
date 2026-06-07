import logging
import sys

from persistence.base import Base
from persistence.engine import create_db_engine, create_session_factory
import persistence.models  # noqa: F401

from worker_service.config import Settings
from worker_service.poller import JobPoller
from worker_service.processors.stub_processor import StubProcessor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)


def main() -> None:
    settings = Settings()

    engine = create_db_engine(settings.database_url)
    Base.metadata.create_all(engine)

    factory = create_session_factory(engine)
    db = factory()

    processor = StubProcessor(db)
    poller = JobPoller(
        db,
        processor,
        poll_interval_seconds=settings.poll_interval_seconds,
        batch_size=settings.batch_size,
    )

    logger.info("Starting worker service...")
    poller.run()


if __name__ == "__main__":
    main()
