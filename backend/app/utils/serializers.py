from app.models import Document


def serialize_document(document: Document, include_extracted_data: bool = True) -> dict:
    """Convert a document ORM object into the API response shape."""
    return {
        "id": str(document.id),
        "filename": document.filename,
        "file_url": document.file_url,
        "document_type": document.document_type,
        "status": document.status,
        "processing_error": document.processing_error,
        "uploaded_at": document.uploaded_at.isoformat(),
        "processing_started_at": document.processing_started_at.isoformat() if document.processing_started_at else None,
        "processing_completed_at": document.processing_completed_at.isoformat() if document.processing_completed_at else None,
        "extracted_data": _serialize_extracted_data(document) if include_extracted_data else None,
    }


def _serialize_extracted_data(document: Document) -> dict | None:
    """Convert the related extracted data ORM object into the API response shape."""
    if not document.extracted_data:
        return None
    return {
        "id": str(document.extracted_data.id),
        "raw_text": document.extracted_data.raw_text,
        "structured_json": document.extracted_data.structured_json,
        "confidence_score": document.extracted_data.confidence_score,
        "extracted_at": document.extracted_data.extracted_at.isoformat(),
    }
