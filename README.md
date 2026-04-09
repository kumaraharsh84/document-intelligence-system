# Document Intelligence System

An AI-powered full-stack web application for uploading business documents, extracting structured data with OCR + LLM workflows, and managing results through a searchable dashboard.

This repository was built in 3 delivery phases and is now ready for local development, Docker-based demos, and GitHub publication.

## Part 1: Foundation and Core CRUD

Included in this checkpoint:

- Project scaffold for `frontend/` and `backend/`
- Docker Compose for frontend, backend, and PostgreSQL
- FastAPI app with async SQLAlchemy setup
- JWT auth endpoints: register, login, current user
- Document APIs: upload, list, detail, search, delete
- Local storage support with optional S3 wiring
- OCR and AI extraction service stubs with a working `/documents/{id}/extract` flow
- React app shell with login, dashboard, upload, and detail pages

## Part 2: Extraction Hardening

Completed in this checkpoint:

- Improved OCR preprocessing for PDFs and images
- Background extraction execution via FastAPI background tasks
- Extraction status timestamps and error tracking on documents
- Richer structured extraction fields for invoices, resumes, and contracts
- Frontend polling and status-aware document detail rendering

## Part 3: Production Readiness

Completed in this checkpoint:

- Added backend integration tests for auth, document CRUD/search, and extraction workflow
- Hardened backend startup with environment-aware secret validation
- Replaced wildcard CORS with configurable origin allowlists
- Improved Docker Compose readiness with health checks and dependency conditions
- Reviewed the codebase for portability issues and switched ORM UUID columns to database-agnostic types

## Features

- JWT-based user registration and login
- PDF and image upload with validation
- OCR text extraction with Tesseract
- AI-assisted structured extraction for invoices, resumes, and contracts
- PostgreSQL-backed metadata and extracted data storage
- Dashboard with search, filtering, status badges, and detail pages
- Docker Compose setup for frontend, backend, and database
- Backend integration tests for auth, documents, and extraction

## Quick Start

1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build`.
3. Open the frontend at `http://localhost:3000`.
4. Open the backend at `http://localhost:8000/docs`.
5. Run backend tests with `python -m pytest backend/tests -q` after installing backend dependencies.

## GitHub Safety

- Commit `.env.example`, never commit `.env`
- Do not commit uploaded files, local test artifacts, or cache folders
- Rotate any secret immediately if it was ever pasted into a tracked file
- Review screenshots before publishing to avoid exposing personal email addresses or document contents

## Environment Variables

```env
POSTGRES_USER=docuser
POSTGRES_PASSWORD=docpassword
POSTGRES_DB=docdb
DATABASE_URL=postgresql+asyncpg://docuser:docpassword@db:5432/docdb
SECRET_KEY=replace_with_a_long_random_secret
ACCESS_TOKEN_EXPIRE_MINUTES=1440
APP_ENV=development
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_BUCKET_NAME=
AWS_REGION=us-east-1
OPENAI_API_KEY=
GOOGLE_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
OCR_ENGINE=tesseract
AI_PROVIDER=openai
STORAGE_BACKEND=local
LOCAL_UPLOAD_DIR=./backend/uploads
MAX_FILE_SIZE_MB=10
VITE_API_BASE_URL=http://localhost:8000/api
```

## API Endpoints

- `POST /api/users/register`
- `POST /api/users/login`
- `GET /api/users/me`
- `GET /api/documents`
- `GET /api/documents/search?q=keyword`
- `GET /api/documents/{id}`
- `POST /api/documents/upload`
- `POST /api/documents/{id}/extract`
- `DELETE /api/documents/{id}`

## Notes

- API responses follow the shared `success/data/message/error` contract.
- Extraction now runs in background tasks and updates document processing timestamps and error state.
- Local file storage is the default development path. S3 support is scaffolded and can be used for persisted uploads.
- In production, set a real `SECRET_KEY`, restrict `CORS_ORIGINS`, and consider replacing in-process background tasks with a dedicated worker queue.

## Portfolio Summary

Document Intelligence System is a full-stack AI document processing platform built with React, FastAPI, PostgreSQL, and Docker. It supports secure authentication, file upload, OCR-based text extraction, AI-powered field parsing, searchable document management, and a responsive dashboard experience suitable for demos, academic projects, and portfolio presentation.
