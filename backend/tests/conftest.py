import io
import os
import shutil
import tempfile
import uuid
from pathlib import Path

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./backend-test-bootstrap.db"
os.environ["SECRET_KEY"] = "test-secret-key"

from app.config import settings
from app import database as database_module
from app.database import Base, get_db
from app.main import app


@pytest_asyncio.fixture
async def test_session_factory(monkeypatch):
    """Create an isolated async database session factory for each test."""
    workspace_temp_dir = Path.cwd() / ".test-artifacts" / str(uuid.uuid4())
    workspace_temp_dir.mkdir(parents=True, exist_ok=True)
    database_path = workspace_temp_dir / "test.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}", future=True)
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    monkeypatch.setattr(database_module, "engine", engine)
    monkeypatch.setattr(database_module, "AsyncSessionLocal", session_factory)
    monkeypatch.setattr(settings, "storage_backend", "local")
    monkeypatch.setattr(settings, "local_upload_dir", str(workspace_temp_dir / "uploads"))
    monkeypatch.setattr(settings, "max_file_size_mb", 10)
    monkeypatch.setattr(settings, "secret_key", "test-secret-key")

    yield session_factory

    await engine.dispose()
    shutil.rmtree(workspace_temp_dir, ignore_errors=True)


@pytest_asyncio.fixture
async def client(test_session_factory):
    """Create an HTTP client with the application's database dependency overridden."""

    async def override_get_db():
        """Yield test database sessions to API handlers."""
        async with test_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as async_client:
            yield async_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_headers(client):
    """Register a test user and return bearer headers for authenticated requests."""
    response = await client.post("/api/users/register", json={"email": "tester@example.com", "password": "strongpass"})
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def make_upload_file(name: str = "sample.pdf", content: bytes = b"%PDF-1.4 test document") -> dict:
    """Build a multipart-compatible upload file tuple for tests."""
    return {"file": (name, io.BytesIO(content), "application/pdf")}
