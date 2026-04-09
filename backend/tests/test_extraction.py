import pytest

from app.routes import extract as extract_route

from .conftest import make_upload_file


@pytest.mark.asyncio
async def test_document_extraction_flow(client, auth_headers, test_session_factory, monkeypatch):
    """Verify extraction queuing, background execution, and persisted structured output."""
    monkeypatch.setattr(extract_route, "AsyncSessionLocal", test_session_factory)

    async def fake_ocr(_: str) -> str:
        """Return deterministic OCR text for the extraction test."""
        return "Invoice ACME Corp Total 1250.00 Date 2026-04-09"

    async def fake_ai(raw_text: str, document_type_hint: str | None = None) -> dict:
        """Return deterministic structured extraction data for the extraction test."""
        return {
            "document_type": document_type_hint or "invoice",
            "extracted_fields": {
                "name": "ACME Corp",
                "date": "2026-04-09",
                "amount": 1250.0,
                "vendor": "ACME Corp",
                "total": 1250.0,
                "parties": [],
                "skills": [],
                "summary": raw_text,
                "line_items": [{"description": "Consulting Services 1250.00"}],
                "keywords": ["Invoice", "ACME"]
            },
            "confidence_score": 0.98
        }

    monkeypatch.setattr(extract_route, "extract_text_with_tesseract", fake_ocr)
    monkeypatch.setattr(extract_route, "extract_structured_data", fake_ai)

    upload_response = await client.post("/api/documents/upload", files=make_upload_file(), headers=auth_headers)
    document_id = upload_response.json()["data"]["id"]

    extract_response = await client.post(
        f"/api/documents/{document_id}/extract",
        json={"document_type_hint": "invoice"},
        headers=auth_headers,
    )
    assert extract_response.status_code == 200
    assert extract_response.json()["data"]["status"] in {"processing", "completed"}

    detail_response = await client.get(f"/api/documents/{document_id}", headers=auth_headers)
    detail_payload = detail_response.json()["data"]
    assert detail_payload["status"] == "completed"
    assert detail_payload["document_type"] == "invoice"
    assert detail_payload["extracted_data"]["structured_json"]["confidence_score"] == 0.98
