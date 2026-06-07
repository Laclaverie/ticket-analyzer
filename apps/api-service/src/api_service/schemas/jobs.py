from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class JobStatusResponse(BaseModel):
    id: str
    receipt_id: str
    status: str
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
