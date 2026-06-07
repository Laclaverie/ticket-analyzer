from pydantic import BaseModel


class UploadReceiptResponse(BaseModel):
    receipt_id: str
    job_id: str
    message: str = "Receipt uploaded and queued for processing."
