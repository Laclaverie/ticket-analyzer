from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class JobStatusResponse(BaseModel):
    id: str
    receipt_id: str
    status: str
    error_message: Optional[str]
    retry_count: int
    max_attempts: int
    next_retry_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
