from datetime import datetime
from pydantic import BaseModel

class WorkerStatusResponse(BaseModel):
    worker_id: str
    processor_kind: str
    last_heartbeat: datetime
    status: str
    is_active: bool

    model_config = {"from_attributes": True}

class SystemStatusResponse(BaseModel):
    workers: list[WorkerStatusResponse]
    server_time: datetime
