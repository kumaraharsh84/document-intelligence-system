import pytest

from .conftest import make_upload_file


@pytest.mark.asyncio
async def test_document_upload_list_search_and_delete(client, auth_headers):
    """Verify the document CRUD and search endpoints for an authenticated user."""
    upload_response = await client.post("/api/documents/upload", files=make_upload_file(), headers=auth_headers)
    assert upload_response.status_code == 200
    upload_payload = upload_response.json()["data"]
    document_id = upload_payload["id"]
    assert upload_payload["status"] == "pending"

    list_response = await client.get("/api/documents", headers=auth_headers)
    assert list_response.status_code == 200
    assert len(list_response.json()["data"]) == 1

    detail_response = await client.get(f"/api/documents/{document_id}", headers=auth_headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["data"]["filename"] == "sample.pdf"

    search_response = await client.get("/api/documents/search", params={"q": "sample"}, headers=auth_headers)
    assert search_response.status_code == 200
    assert len(search_response.json()["data"]) == 1

    delete_response = await client.delete(f"/api/documents/{document_id}", headers=auth_headers)
    assert delete_response.status_code == 200

    final_list_response = await client.get("/api/documents", headers=auth_headers)
    assert final_list_response.status_code == 200
    assert final_list_response.json()["data"] == []
