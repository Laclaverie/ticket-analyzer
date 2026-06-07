from abc import ABC, abstractmethod


class BaseProcessor(ABC):
    """
    Strategy interface for receipt processing.

    To add a new processing strategy (e.g. OCR in Phase 1), subclass this and
    implement `process`. The JobPoller accepts any BaseProcessor — no changes
    to the poller or repositories are required.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for logging and observability."""
        ...

    @abstractmethod
    def process(self, job_id: str) -> None:
        """
        Execute processing for the given job.
        Must not commit the database session — the poller manages transactions.
        Raise any exception to signal failure; the poller will mark the job FAILED.
        """
        ...
