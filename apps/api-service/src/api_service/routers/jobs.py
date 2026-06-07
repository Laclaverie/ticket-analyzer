from fastapi import APIRouter, HTTPException

from api_service.dependencies import DbDep
from api_service.repositories.job_repository import JobRepository
from api_service.schemas.jobs import JobStatusResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job(job_id: str, db: DbDep = None) -> JobStatusResponse:
    repo = JobRepository(db)
    job = repo.find_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(
        id=job.id,
        receipt_id=job.receipt_id,
        status=job.status.value,
        error_message=job.error_message,
        retry_count=job.retry_count,
        max_attempts=job.max_attempts,
        next_retry_at=job.next_retry_at,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
