from fastapi import APIRouter, File, UploadFile, status

from api_service.dependencies import DbDep, SettingsDep
from api_service.repositories.receipt_repository import ReceiptRepository
from api_service.repositories.job_repository import JobRepository
from api_service.services.ingestion_service import IngestionService
from api_service.schemas.receipt import UploadReceiptResponse

router = APIRouter(prefix="/receipts", tags=["receipts"])


@router.post(
    "/upload",
    response_model=UploadReceiptResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_receipt(
    file: UploadFile = File(...),
    db: DbDep = None,
    settings: SettingsDep = None,
) -> UploadReceiptResponse:
    receipt_repo = ReceiptRepository(db)
    job_repo = JobRepository(db)
    service = IngestionService(receipt_repo, job_repo, settings.storage_path)
    result = await service.ingest(file)
    db.commit()
    return result
