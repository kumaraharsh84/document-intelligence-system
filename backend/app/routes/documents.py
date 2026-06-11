import os
import uuid
import logging
import io
import csv

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
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


@router.get("/export")
async def export_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export all documents and structured data to a CSV file."""
    try:
        query = (
            select(Document)
            .options(selectinload(Document.extracted_data))
            .where(Document.user_id == current_user.id)
            .order_by(Document.uploaded_at.desc())
        )
        result = await db.execute(query)
        documents = result.scalars().all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Filename", "Status", "Type", "Uploaded At", "Extracted Name", "Extracted Date", "Extracted Amount", "Extracted Vendor", "Confidence"])
        
        for doc in documents:
            row = [
                str(doc.id),
                doc.filename,
                doc.status,
                doc.document_type or "",
                doc.uploaded_at.isoformat(),
            ]
            if doc.extracted_data and isinstance(doc.extracted_data.structured_json, dict):
                fields = doc.extracted_data.structured_json.get("extracted_fields", {})
                row.extend([
                    fields.get("name") or "",
                    fields.get("date") or "",
                    fields.get("amount") or "",
                    fields.get("vendor") or "",
                    doc.extracted_data.confidence_score or 0.0
                ])
            else:
                row.extend(["", "", "", "", ""])
                
            writer.writerow(row)
            
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=documents_export.csv"}
        )
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
async def upload_documents(
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Validate and store multiple user-uploaded documents."""
    saved_documents = []
    
    for file in files:
        file_url: str | None = None
        try:
            extension = os.path.splitext(file.filename or "")[1].lower()
            if extension not in ALLOWED_EXTENSIONS:
                continue # Skip unsupported
            if file.size and file.size > settings.max_file_size_mb * 1024 * 1024:
                continue # Skip too large
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
            saved_documents.append(serialize_document(document, include_extracted_data=False))
        except Exception as exc:
            await db.rollback()
            if file_url:
                try:
                    await delete_upload(file_url)
                except Exception:
                    logger.exception("Failed to clean up uploaded file after database failure")
            # We continue processing the other files even if one fails
            
    if not saved_documents:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid files were uploaded")
         
    return api_response(
        True,
        saved_documents,
        f"{len(saved_documents)} documents uploaded successfully",
        None,
    )


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
