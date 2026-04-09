# Document Intelligence System

AI-powered full-stack document processing platform built with React, FastAPI, PostgreSQL, and Docker.

This application lets users upload business documents such as invoices, resumes, and contracts, extract structured data using OCR and AI-assisted parsing, and manage results through a searchable dashboard.

## Features

- JWT-based user registration and login
- PDF and image upload with validation
- OCR text extraction using Tesseract
- AI-assisted structured field extraction
- PostgreSQL-backed document and extraction storage
- Searchable dashboard with status tracking
- Background extraction workflow
- Docker Compose setup for frontend, backend, and database
- Backend integration tests for auth, document flows, and extraction

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | React.js + Tailwind CSS | Login, upload, dashboard, detail pages |
| Backend | FastAPI | Async REST API |
| Database | PostgreSQL + SQLAlchemy | Users, documents, extracted data |
| OCR | Tesseract OCR | Raw text extraction from files |
| AI Extraction | OpenAI-ready structured parsing with fallback heuristics | Structured JSON generation |
| File Storage | Local filesystem or AWS S3 | Uploaded document storage |
| Authentication | JWT | Secure user sessions |
| Containers | Docker + Docker Compose | Consistent local deployment |
| Validation | Pydantic | Request and schema validation |

## System Architecture

```text
User
  -> React Frontend (3000)
  -> FastAPI Backend (8000)
  -> OCR + AI Extraction
  -> PostgreSQL / Local Storage or S3
```

## Project Structure

```text
document-intelligence-system/
|-- frontend/
|   `-- src/
|       |-- components/
|       `-- pages/
|-- backend/
|   |-- app/
|   |   |-- routes/
|   |   |-- services/
|   |   |-- models.py
|   |   |-- schemas.py
|   |   `-- main.py
|   `-- tests/
|-- docker-compose.yml
|-- .env.example
`-- README.md
```

## Quick Start

1. Copy `.env.example` to `.env`
2. Run `docker compose up --build`
3. Open the frontend at `http://localhost:3000`
4. Open the API docs at `http://localhost:8000/docs`
5. Run backend tests with `python -m pytest backend/tests -q`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users/register` | Create a new user account |
| POST | `/api/users/login` | Login and receive JWT token |
| GET | `/api/users/me` | Get current logged-in user |
| GET | `/api/documents` | List uploaded documents |
| GET | `/api/documents/search?q=` | Search documents by keyword |
| GET | `/api/documents/{id}` | Get one document with extracted data |
| POST | `/api/documents/upload` | Upload a new PDF or image |
| POST | `/api/documents/{id}/extract` | Trigger extraction |
| DELETE | `/api/documents/{id}` | Delete a document |

## Database Schema

### Users

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| email | String | Unique user email |
| hashed_password | String | Secure password hash |
| created_at | DateTime | Account creation time |

### Documents

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to users |
| filename | String | Original file name |
| file_url | String | Stored file path or URL |
| document_type | String | invoice / resume / contract |
| status | String | pending / processing / completed / failed |
| uploaded_at | DateTime | Upload timestamp |

### Extracted Data

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| document_id | UUID | Foreign key to documents |
| raw_text | Text | Full OCR output |
| structured_json | JSONB | Parsed structured fields |
| confidence_score | Float | Value from 0.0 to 1.0 |

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

## Delivery Phases

### Phase 1: Foundation and Core CRUD

- Project scaffold with Docker Compose
- FastAPI backend with async SQLAlchemy
- JWT auth endpoints
- Upload, list, search, detail, and delete APIs
- React pages for login, dashboard, upload, and detail

### Phase 2: Extraction Hardening

- OCR preprocessing improvements
- Background extraction flow
- Better structured fields for invoices, resumes, and contracts
- Frontend polling and status-aware extraction UI

### Phase 3: Production Readiness

- Backend integration tests
- Environment-aware secret validation
- Configurable CORS allowlist
- Docker health checks
- Portable UUID handling across environments

## GitHub Safety

- Commit `.env.example`, never commit `.env`
- Keep uploaded files, cache folders, and test artifacts out of Git
- Rotate any secret immediately if it was ever exposed
- Review screenshots and sample documents before publishing

## Portfolio Summary

Document Intelligence System is a full-stack AI document processing platform that demonstrates secure authentication, file upload workflows, OCR-based extraction, AI-assisted structured parsing, document search, and dashboard visualization in a Dockerized architecture.
