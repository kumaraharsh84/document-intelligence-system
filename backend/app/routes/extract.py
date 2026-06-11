from datetime import datetime, timezone
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user
from app.database import AsyncSessionLocal, get_db
from app.models import Document, ExtractedData, User
from app.schemas import ExtractRequest
from app.services.ai_extraction import extract_structured_data
from app.services.storage_service import open_local_copy
from app.services.parser_service import extract_text_from_file
from app.utils.response import api_response
from app.utils.serializers import serialize_document

router = APIRouter(tags=["extraction"])


@router.post("/documents/{document_id}/extract")
async def extract_document_data(
    document_id: uuid.UUID,
    payload: ExtractRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Queue OCR and structured extraction for a stored document."""
    try:
        result = await db.execute(
            select(Document)
            .options(selectinload(Document.extracted_data))
            .where(Document.id == document_id, Document.user_id == current_user.id)
        )
        document = result.scalar_one_or_none()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        if document.status == "processing":
            return api_response(True, serialize_document(document), "Document extraction is already in progress", None)
        document.status = "processing"
        document.processing_error = None
        document.processing_started_at = datetime.now(timezone.utc)
        document.processing_completed_at = None
        await db.commit()
        await db.refresh(document)
        background_tasks.add_task(run_extraction_job, document.id, current_user.id, payload.document_type_hint)
        return api_response(
            True,
            serialize_document(document),
            "Extraction queued successfully",
            None,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


async def run_extraction_job(document_id: uuid.UUID, user_id: uuid.UUID, document_type_hint: str | None = None) -> None:
    """Process OCR and structured extraction in the background and persist the result."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Document)
            .options(selectinload(Document.extracted_data))
            .where(Document.id == document_id, Document.user_id == user_id)
        )
        document = result.scalar_one_or_none()
        if not document:
            return
        try:
            async with open_local_copy(document.file_url) as local_path:
                raw_text = await extract_text_from_file(local_path)
            structured = await extract_structured_data(raw_text, document_type_hint or document.document_type)

            if document.extracted_data:
                document.extracted_data.raw_text = raw_text
                document.extracted_data.structured_json = structured
                document.extracted_data.confidence_score = structured.get("confidence_score", 0.0)
            else:
                document.extracted_data = ExtractedData(
                    raw_text=raw_text,
                    structured_json=structured,
                    confidence_score=structured.get("confidence_score", 0.0),
                )
            document.document_type = structured.get("document_type", document_type_hint)
            document.status = "completed"
            document.processing_error = None
            document.processing_completed_at = datetime.now(timezone.utc)
            db.add(document)
            await db.commit()
        except Exception as exc:
            document.status = "failed"
            document.processing_error = str(exc)
            document.processing_completed_at = datetime.now(timezone.utc)
            db.add(document)
            await db.commit()
