from datetime import datetime, timezone, timedelta
from fastapi import APIRouter

from api_service.dependencies import DbDep
from api_service.schemas.system import SystemStatusResponse, WorkerStatusResponse
from persistence.models.worker_status import WorkerStatusORM

router = APIRouter(prefix="/system", tags=["system"])

@router.get("/status", response_model=SystemStatusResponse)
def get_system_status(db: DbDep = None) -> SystemStatusResponse:
    workers_orm = db.query(WorkerStatusORM).all()

    now = datetime.now(timezone.utc)
    # Consider a worker inactive if no heartbeat for 30 seconds
    threshold = now - timedelta(seconds=30)

    worker_responses = []
    for w in workers_orm:
        # Ensure w.last_heartbeat is offset-aware
        heartbeat = w.last_heartbeat
        if heartbeat.tzinfo is None:
            heartbeat = heartbeat.replace(tzinfo=timezone.utc)

        is_active = heartbeat > threshold
        worker_responses.append(WorkerStatusResponse(
            worker_id=w.worker_id,
            processor_kind=w.processor_kind,
            last_heartbeat=heartbeat,
            status="online" if is_active else "offline",
            is_active=is_active
        ))

    return SystemStatusResponse(
        workers=worker_responses,
        server_time=now
    )
