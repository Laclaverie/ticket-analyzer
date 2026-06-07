import io

from persistence.models.processing_job import ProcessingJobORM


def test_upload_receipt_returns_201(client):
    response = client.post(
        "/receipts/upload",
        files={"file": ("receipt.jpg", io.BytesIO(b"fake image"), "image/jpeg")},
    )
    assert response.status_code == 201


def test_upload_receipt_response_contains_receipt_id(client):
    response = client.post(
        "/receipts/upload",
        files={"file": ("receipt.jpg", io.BytesIO(b"fake image"), "image/jpeg")},
    )
    assert "receipt_id" in response.json()


def test_upload_receipt_response_contains_job_id(client):
    response = client.post(
        "/receipts/upload",
        files={"file": ("receipt.jpg", io.BytesIO(b"fake image"), "image/jpeg")},
    )
    assert "job_id" in response.json()


def test_upload_receipt_ids_are_non_empty(client):
    response = client.post(
        "/receipts/upload",
        files={"file": ("receipt.jpg", io.BytesIO(b"data"), "image/jpeg")},
    )
    data = response.json()
    assert data["receipt_id"]
    assert data["job_id"]


def test_upload_without_file_returns_422(client):
    response = client.post("/receipts/upload")
    assert response.status_code == 422


def test_upload_creates_pending_job_in_db(client, db_session):
    response = client.post(
        "/receipts/upload",
        files={"file": ("receipt.jpg", io.BytesIO(b"data"), "image/jpeg")},
    )
    job_id = response.json()["job_id"]

    job = db_session.get(ProcessingJobORM, job_id)
    assert job is not None
    assert job.status == "pending"


def test_upload_stores_image_file(client, test_settings):
    from pathlib import Path

    response = client.post(
        "/receipts/upload",
        files={"file": ("receipt.jpg", io.BytesIO(b"image data"), "image/jpeg")},
    )
    receipt_id = response.json()["receipt_id"]
    image_dir = Path(test_settings.storage_path) / receipt_id
    assert image_dir.exists()
    files = list(image_dir.iterdir())
    assert len(files) == 1
