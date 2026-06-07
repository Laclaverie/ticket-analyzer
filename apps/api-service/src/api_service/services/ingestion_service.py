import hashlib
from pathlib import Path

from fastapi import UploadFile

from api_service.repositories.receipt_repository import ReceiptRepository
from api_service.repositories.job_repository import JobRepository
from api_service.schemas.receipt import UploadReceiptResponse


class IngestionService:
    """
    Orchestrates the receipt upload flow.
    Responsibilities: file storage, receipt record, image record, job enqueue.
    Does NOT commit the transaction — that is the router's responsibility.
    """

    def __init__(
        self,
        receipt_repo: ReceiptRepository,
        job_repo: JobRepository,
        storage_path: str,
    ) -> None:
        self._receipt_repo = receipt_repo
        self._job_repo = job_repo
        self._storage_path = Path(storage_path)

    async def ingest(self, file: UploadFile) -> UploadReceiptResponse:
        contents = await file.read()
        file_hash = hashlib.sha256(contents).hexdigest()

        receipt = self._receipt_repo.save(store=None, currency="EUR")

        image_path = self._store_image(receipt.id, file.filename or "upload", contents)
        self._receipt_repo.save_image(receipt.id, str(image_path), file_hash)

        job = self._job_repo.create(receipt.id)

        return UploadReceiptResponse(receipt_id=receipt.id, job_id=job.id)

    def _store_image(self, receipt_id: str, filename: str, contents: bytes) -> Path:
        dest_dir = self._storage_path / receipt_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        suffix = Path(filename).suffix or ".bin"
        dest_path = dest_dir / f"original{suffix}"
        dest_path.write_bytes(contents)
        return dest_path
