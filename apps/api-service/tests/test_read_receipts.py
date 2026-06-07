import io


def test_list_receipts_empty(client):
    response = client.get("/receipts")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1


def test_list_receipts_after_upload(client):
    client.post(
        "/receipts/upload",
        files={"file": ("r.jpg", io.BytesIO(b"img"), "image/jpeg")},
    )
    response = client.get("/receipts")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1


def test_list_receipts_pagination(client):
    for _ in range(3):
        client.post(
            "/receipts/upload",
            files={"file": ("r.jpg", io.BytesIO(b"img"), "image/jpeg")},
        )
    response = client.get("/receipts?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2


def test_get_receipt_returns_detail(client):
    upload = client.post(
        "/receipts/upload",
        files={"file": ("r.jpg", io.BytesIO(b"img"), "image/jpeg")},
    )
    receipt_id = upload.json()["receipt_id"]

    response = client.get(f"/receipts/{receipt_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == receipt_id
    assert "images" in data
    assert len(data["images"]) == 1


def test_get_receipt_returns_404_for_unknown(client):
    response = client.get("/receipts/nonexistent-id")
    assert response.status_code == 404


def test_get_receipt_items_empty_before_processing(client):
    upload = client.post(
        "/receipts/upload",
        files={"file": ("r.jpg", io.BytesIO(b"img"), "image/jpeg")},
    )
    receipt_id = upload.json()["receipt_id"]

    response = client.get(f"/receipts/{receipt_id}/items")
    assert response.status_code == 200
    data = response.json()
    assert data["receipt_id"] == receipt_id
    assert data["items"] == []


def test_get_receipt_items_returns_404_for_unknown(client):
    response = client.get("/receipts/nonexistent-id/items")
    assert response.status_code == 404
