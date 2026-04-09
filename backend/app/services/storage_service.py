import os
import tempfile
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import boto3
from fastapi import UploadFile

from app.config import settings


async def save_upload(file: UploadFile) -> str:
    """Persist an uploaded file to local storage or S3 and return its URL."""
    if settings.storage_backend.lower() == "s3" and settings.aws_bucket_name:
        return await _save_to_s3(file)
    return await _save_to_local(file)


async def delete_upload(file_url: str) -> None:
    """Delete a stored file from local storage or S3 if it exists."""
    if settings.storage_backend.lower() == "s3" and settings.aws_bucket_name:
        await _delete_from_s3(file_url)
    else:
        await _delete_from_local(file_url)


@asynccontextmanager
async def open_local_copy(file_url: str):
    """Yield a readable local filesystem path for either local or S3-backed files."""
    if settings.storage_backend.lower() == "s3" and settings.aws_bucket_name and file_url.startswith("http"):
        temp_path = await _download_s3_to_temp(file_url)
        try:
            yield temp_path
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        return
    yield file_url


async def _save_to_local(file: UploadFile) -> str:
    """Write an uploaded file to the local uploads directory."""
    upload_dir = Path(settings.local_upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    extension = Path(file.filename or "").suffix
    safe_name = f"{uuid.uuid4()}{extension}"
    target_path = upload_dir / safe_name
    contents = await file.read()
    target_path.write_bytes(contents)
    await file.seek(0)
    return str(target_path)


async def _delete_from_local(file_url: str) -> None:
    """Remove a local uploaded file when it is deleted from the system."""
    if file_url and os.path.exists(file_url):
        os.remove(file_url)


async def _save_to_s3(file: UploadFile) -> str:
    """Upload an incoming file to an S3 bucket and return the object URL."""
    client = boto3.client(
        "s3",
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
    )
    extension = Path(file.filename or "").suffix
    key = f"documents/{uuid.uuid4()}{extension}"
    client.upload_fileobj(file.file, settings.aws_bucket_name, key)
    await file.seek(0)
    return f"https://{settings.aws_bucket_name}.s3.{settings.aws_region}.amazonaws.com/{key}"


async def _delete_from_s3(file_url: str) -> None:
    """Delete an uploaded S3 object using the file URL."""
    if not file_url:
        return
    key = file_url.split(".amazonaws.com/")[-1]
    client = boto3.client(
        "s3",
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
    )
    client.delete_object(Bucket=settings.aws_bucket_name, Key=key)


async def _download_s3_to_temp(file_url: str) -> str:
    """Download an S3 object to a temporary local file for OCR processing."""
    key = file_url.split(".amazonaws.com/")[-1]
    suffix = Path(key).suffix
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.close()
    client = boto3.client(
        "s3",
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
    )
    client.download_file(settings.aws_bucket_name, key, temp_file.name)
    return temp_file.name
