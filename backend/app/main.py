from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.routes.documents import router as documents_router
from app.routes.extract import router as extract_router
from app.routes.users import router as users_router
from app.utils.response import api_response


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize application state and validate runtime settings at startup."""
    if settings.is_production and settings.secret_key == "change-me":
        raise RuntimeError("SECRET_KEY must be changed before running in production")
    await init_db()
    yield


app = FastAPI(title="Document Intelligence System", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list if settings.cors_origin_list else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    """Normalize FastAPI HTTP exceptions into the shared response format."""
    return JSONResponse(
        status_code=exc.status_code,
        content=api_response(False, None, "Request failed", str(exc.detail)),
    )


@app.get("/health")
async def health_check() -> dict:
    """Return a lightweight health check response."""
    return api_response(True, {"status": "ok"}, "Service is healthy", None)


app.include_router(users_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(extract_router, prefix="/api")
