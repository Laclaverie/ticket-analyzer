from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from api_service.dependencies import DbDep, SettingsDep
from api_service.repositories.receipt_repository import ReceiptRepository
from api_service.repositories.job_repository import JobRepository
from api_service.services.ingestion_service import IngestionService
from api_service.schemas.receipt import (
    ReceiptDetailResponse,
    ReceiptImageResponse,
    ReceiptListResponse,
    ReceiptResponse,
    UploadReceiptResponse,
)
from api_service.schemas.items import NormalizedItemResponse, ReceiptItemsResponse

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


@router.get("", response_model=ReceiptListResponse)
def list_receipts(
    db: DbDep = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> ReceiptListResponse:
    repo = ReceiptRepository(db)
    offset = (page - 1) * page_size
    rows, total = repo.list_all(offset=offset, limit=page_size)
    return ReceiptListResponse(
        items=[ReceiptResponse.model_validate(r) for r in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{receipt_id}", response_model=ReceiptDetailResponse)
def get_receipt(receipt_id: str, db: DbDep = None) -> ReceiptDetailResponse:
    repo = ReceiptRepository(db)
    orm = repo.find_detail_orm(receipt_id)
    if not orm:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return ReceiptDetailResponse(
        id=orm.id,
        store=orm.store,
        purchase_date=orm.purchase_date,
        total_amount=orm.total_amount,
        currency=orm.currency,
        created_at=orm.created_at,
        images=[ReceiptImageResponse.model_validate(img) for img in orm.images],
    )


@router.get("/{receipt_id}/items", response_model=ReceiptItemsResponse)
def get_receipt_items(receipt_id: str, db: DbDep = None) -> ReceiptItemsResponse:
    repo = ReceiptRepository(db)
    if not repo.find_detail_orm(receipt_id):
        raise HTTPException(status_code=404, detail="Receipt not found")
    items = repo.find_normalized_items(receipt_id)

    response_items = []
    for i in items:
        resp = NormalizedItemResponse.model_validate(i)
        resp.raw_text = i.raw_item.raw_text if i.raw_item else None
        response_items.append(resp)

    return ReceiptItemsResponse(
        receipt_id=receipt_id,
        items=response_items,
    )
