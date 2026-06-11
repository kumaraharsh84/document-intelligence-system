import os
import uuid
import logging

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.models import Document, ExtractedData, User
from app.services.storage_service import delete_upload, save_upload
from app.utils.response import api_response
from app.utils.serializers import serialize_document

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".doc", ".docx", ".xls", ".xlsx"}


async def _get_owned_document(document_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> Document:
    """Fetch a document owned by the current user or raise a 404 error."""
    result = await db.execute(
        select(Document)
        .options(selectinload(Document.extracted_data))
        .where(Document.id == document_id, Document.user_id == user_id)
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.get("")
async def list_documents(
    document_type: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """List the current user's documents with optional type filtering."""
    try:
        query = (
            select(Document)
            .options(selectinload(Document.extracted_data))
            .where(Document.user_id == current_user.id)
            .order_by(Document.uploaded_at.desc())
        )
        if document_type:
            query = query.where(Document.document_type == document_type)
        result = await db.execute(query)
        documents = result.scalars().all()
        data = [serialize_document(item, include_extracted_data=True) for item in documents]
        return api_response(True, data, "Documents loaded successfully", None)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/search")
async def search_documents(
    q: str = Query(..., min_length=1),
    document_type: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Search document names and extracted OCR text for the current user."""
    try:
        query = (
            select(Document)
            .outerjoin(ExtractedData, ExtractedData.document_id == Document.id)
            .options(selectinload(Document.extracted_data))
            .where(Document.user_id == current_user.id)
            .where(or_(Document.filename.ilike(f"%{q}%"), ExtractedData.raw_text.ilike(f"%{q}%")))
            .order_by(Document.uploaded_at.desc())
        )
        if document_type:
            query = query.where(Document.document_type == document_type)
        result = await db.execute(query)
        documents = result.scalars().unique().all()
        data = [serialize_document(item, include_extracted_data=False) for item in documents]
        return api_response(True, data, "Search completed successfully", None)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{document_id}")
async def get_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Return one document with its extracted data."""
    try:
        document = await _get_owned_document(document_id, current_user.id, db)
        data = serialize_document(document, include_extracted_data=True)
        return api_response(True, data, "Document loaded successfully", None)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Validate and store a user-uploaded document."""
    file_url: str | None = None
    try:
        extension = os.path.splitext(file.filename or "")[1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")
        if file.size and file.size > settings.max_file_size_mb * 1024 * 1024:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File exceeds size limit")
        file_url = await save_upload(file)
        document = Document(
            user_id=current_user.id,
            filename=file.filename or "uploaded-file",
            file_url=file_url,
            status="pending",
            processing_error=None,
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)
        return api_response(
            True,
            serialize_document(document, include_extracted_data=False),
            "Document uploaded successfully",
            None,
        )
    except HTTPException:
        if file_url:
            try:
                await delete_upload(file_url)
            except Exception:
                logger.exception("Failed to clean up uploaded file after HTTP error")
        raise
    except Exception as exc:
        await db.rollback()
        if file_url:
            try:
                await delete_upload(file_url)
            except Exception:
                logger.exception("Failed to clean up uploaded file after database failure")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/{document_id}")
async def delete_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Delete a document, its extracted data, and the stored file."""
    try:
        document = await _get_owned_document(document_id, current_user.id, db)
        file_url = document.file_url
        await db.delete(document)
        await db.commit()
        try:
            await delete_upload(file_url)
        except Exception:
            logger.exception("Failed to delete stored file after document row was removed")
        return api_response(True, {"id": str(document_id)}, "Document deleted successfully", None)
    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc
