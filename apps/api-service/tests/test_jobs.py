import io


def test_get_job_returns_pending_status(client):
    upload = client.post(
        "/receipts/upload",
        files={"file": ("r.jpg", io.BytesIO(b"img"), "image/jpeg")},
    )
    job_id = upload.json()["job_id"]

    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == job_id
    assert data["status"] == "pending"
    assert data["error_message"] is None
    assert data["retry_count"] == 0
    assert data["max_attempts"] == 3


def test_get_job_returns_receipt_id(client):
    upload = client.post(
        "/receipts/upload",
        files={"file": ("r.jpg", io.BytesIO(b"img"), "image/jpeg")},
    )
    job_id = upload.json()["job_id"]
    receipt_id = upload.json()["receipt_id"]

    response = client.get(f"/jobs/{job_id}")
    assert response.json()["receipt_id"] == receipt_id


def test_get_job_includes_retry_metadata(client):
    upload = client.post(
        "/receipts/upload",
        files={"file": ("r.jpg", io.BytesIO(b"img"), "image/jpeg")},
    )
    job_id = upload.json()["job_id"]

    data = client.get(f"/jobs/{job_id}").json()
    assert "retry_count" in data
    assert "max_attempts" in data
    assert "next_retry_at" in data


def test_get_job_returns_404_for_unknown(client):
    response = client.get("/jobs/nonexistent-id")
    assert response.status_code == 404
