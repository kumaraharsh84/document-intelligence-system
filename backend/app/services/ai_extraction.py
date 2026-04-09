import json
import re

import httpx
from dateutil import parser as date_parser

from app.config import settings


async def extract_structured_data(raw_text: str, document_type_hint: str | None = None) -> dict:
    """Convert OCR text into a normalized structured payload using an AI provider or fallback rules."""
    if settings.ai_provider.lower() == "openai" and settings.openai_api_key:
        try:
            return await _extract_with_openai(raw_text, document_type_hint)
        except Exception:
            return _fallback_extraction(raw_text, document_type_hint)
    return _fallback_extraction(raw_text, document_type_hint)


async def _extract_with_openai(raw_text: str, document_type_hint: str | None = None) -> dict:
    """Call the OpenAI Responses API to produce structured document data."""
    prompt = _build_extraction_prompt(raw_text, document_type_hint)
    headers = {"Authorization": f"Bearer {settings.openai_api_key}", "Content-Type": "application/json"}
    payload = {
        "model": settings.openai_model,
        "input": prompt,
        "text": {
            "format": {
                "type": "json_schema",
                "name": "document_extraction",
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "document_type": {"type": "string"},
                        "extracted_fields": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "name": {"type": ["string", "null"]},
                                "date": {"type": ["string", "null"]},
                                "amount": {"type": ["number", "null"]},
                                "vendor": {"type": ["string", "null"]},
                                "total": {"type": ["number", "null"]},
                                "parties": {"type": "array", "items": {"type": "string"}},
                                "skills": {"type": "array", "items": {"type": "string"}},
                                "summary": {"type": ["string", "null"]},
                                "line_items": {"type": "array", "items": {"type": "object"}},
                                "keywords": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["name", "date", "amount", "vendor", "total", "parties", "skills", "summary", "line_items", "keywords"]
                        },
                        "confidence_score": {"type": "number"}
                    },
                    "required": ["document_type", "extracted_fields", "confidence_score"]
                }
            }
        }
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post("https://api.openai.com/v1/responses", headers=headers, json=payload)
        response.raise_for_status()
        content = response.json().get("output", [])
        text_chunks = []
        for item in content:
            for chunk in item.get("content", []):
                if chunk.get("type") == "output_text":
                    text_chunks.append(chunk.get("text", ""))
        return _normalize_extraction(json.loads("".join(text_chunks)), raw_text, document_type_hint)
    
    
def _build_extraction_prompt(raw_text: str, document_type_hint: str | None = None) -> str:
    """Create a focused extraction prompt with explicit field rules."""
    return (
        "Extract structured data from the document text. "
        "Classify document_type as invoice, resume, contract, or unknown. "
        "Return null for missing scalar fields, empty arrays for missing lists, "
        "and keep confidence_score between 0 and 1. "
        "Use concise summaries and deduplicated keywords. "
        f"Document type hint: {document_type_hint or 'unknown'}. "
        f"Document text:\n{raw_text[:14000]}"
    )


def _fallback_extraction(raw_text: str, document_type_hint: str | None = None) -> dict:
    """Build a simple structured payload when an AI provider is unavailable."""
    lowered = raw_text.lower()
    document_type = document_type_hint or "unknown"
    if "invoice" in lowered:
        document_type = "invoice"
    elif "resume" in lowered or "experience" in lowered:
        document_type = "resume"
    elif "agreement" in lowered or "contract" in lowered:
        document_type = "contract"
    date_match = _extract_date(raw_text)
    name = _extract_name(raw_text, document_type)
    vendor = _extract_vendor(raw_text, document_type)
    line_items = _extract_line_items(raw_text) if document_type == "invoice" else []
    skills = _extract_skills(raw_text) if document_type == "resume" else []
    parties = _extract_parties(raw_text) if document_type == "contract" else []
    keywords = _extract_keywords(raw_text)
    amount_value = _extract_amount(raw_text, document_type)
    total_value = amount_value if document_type == "invoice" else None
    extracted = {
        "document_type": document_type,
        "extracted_fields": {
            "name": name,
            "date": date_match,
            "amount": amount_value,
            "vendor": vendor,
            "total": total_value,
            "parties": parties,
            "skills": skills,
            "summary": _extract_summary(raw_text),
            "line_items": line_items,
            "keywords": keywords
        },
        "confidence_score": 0.45
    }
    return _normalize_extraction(extracted, raw_text, document_type_hint)


def _normalize_extraction(payload: dict, raw_text: str, document_type_hint: str | None = None) -> dict:
    """Normalize an extraction payload so the API always returns the expected shape."""
    fields = payload.get("extracted_fields") or {}
    normalized_document_type = payload.get("document_type") or document_type_hint or "unknown"
    if normalized_document_type not in {"invoice", "resume", "contract", "unknown"}:
        normalized_document_type = document_type_hint or "unknown"

    amount_value = _to_float(fields.get("amount"))
    total_value = _to_float(fields.get("total"))
    if normalized_document_type != "invoice":
        amount_value = None
        total_value = None

    normalized = {
        "document_type": normalized_document_type,
        "extracted_fields": {
            "name": fields.get("name") or _extract_name(raw_text, normalized_document_type),
            "date": _extract_date(fields.get("date") or raw_text),
            "amount": amount_value,
            "vendor": fields.get("vendor"),
            "total": total_value,
            "parties": _clean_list(fields.get("parties")),
            "skills": _clean_list(fields.get("skills")),
            "summary": fields.get("summary") or _extract_summary(raw_text),
            "line_items": fields.get("line_items") if isinstance(fields.get("line_items"), list) else [],
            "keywords": _clean_list(fields.get("keywords")) or _extract_keywords(raw_text)
        },
        "confidence_score": min(max(_to_float(payload.get("confidence_score")) or 0.0, 0.0), 1.0)
    }
    return normalized


def _extract_date(text: str | None) -> str | None:
    """Extract and normalize a document date when one can be inferred."""
    if not text:
        return None
    patterns = [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return date_parser.parse(match.group(0), fuzzy=True).date().isoformat()
            except (ValueError, OverflowError):
                return match.group(0)
    return None


def _extract_name(raw_text: str, document_type: str) -> str | None:
    """Infer a likely primary name field from the document text."""
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if not lines:
        return None
    if document_type == "resume":
        for line in lines[:8]:
            if _looks_like_resume_name(line):
                return line[:120]
        return lines[0][:120]
    if document_type == "invoice":
        return next((line[:120] for line in lines if "bill to" in line.lower()), lines[0][:120])
    return lines[0][:120]


def _extract_vendor(raw_text: str, document_type: str) -> str | None:
    """Infer the vendor or issuer from invoice-like documents."""
    if document_type != "invoice":
        return None
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    return lines[0][:120] if lines else None


def _extract_line_items(raw_text: str) -> list[dict]:
    """Create lightweight line items from tabular-looking OCR lines."""
    items = []
    for line in raw_text.splitlines():
        cleaned = line.strip()
        if len(cleaned.split()) >= 2 and re.search(r"\d[\d,]*\.?\d{0,2}", cleaned):
            items.append({"description": cleaned[:160]})
        if len(items) >= 5:
            break
    return items


def _extract_keywords(raw_text: str) -> list[str]:
    """Extract a deduplicated keyword list from OCR text."""
    seen = set()
    keywords = []
    for word in re.findall(r"\b[a-zA-Z][a-zA-Z-]{4,}\b", raw_text):
        lowered = word.lower()
        if lowered not in seen:
            seen.add(lowered)
            keywords.append(word)
        if len(keywords) >= 12:
            break
    return keywords


def _extract_skills(raw_text: str) -> list[str]:
    """Infer resume skills from common technology and business terms."""
    skills_bank = [
        "python", "java", "javascript", "react", "sql", "aws", "docker", "fastapi",
        "communication", "leadership", "excel", "machine learning", "project management",
        "cloud", "cybersecurity", "linux", "git", "kubernetes", "html", "css"
    ]
    lowered = raw_text.lower()
    return [skill for skill in skills_bank if skill in lowered]


def _extract_parties(raw_text: str) -> list[str]:
    """Infer contract parties from lines that look like named participants."""
    parties = []
    for line in raw_text.splitlines():
        cleaned = line.strip()
        if any(keyword in cleaned.lower() for keyword in ["between", "party", "client", "vendor", "company"]):
            parties.append(cleaned[:160])
        if len(parties) >= 5:
            break
    return parties


def _extract_summary(raw_text: str) -> str | None:
    """Build a short summary from the first meaningful lines of OCR text."""
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if not lines:
        return None
    filtered_lines = [line for line in lines if not _looks_like_contact_line(line)]
    source_lines = filtered_lines or lines
    return " ".join(source_lines[:3])[:320]


def _extract_amount(raw_text: str, document_type: str) -> float | None:
    """Extract monetary amounts only for invoice-like documents."""
    if document_type != "invoice":
        return None
    amount_match = re.search(r"(?<!\d)(\d[\d,]*\.?\d{0,2})(?!\d)", raw_text)
    return float(amount_match.group(1).replace(",", "")) if amount_match else None


def _looks_like_resume_name(line: str) -> bool:
    """Estimate whether a line looks like a person's name in a resume."""
    cleaned = line.strip()
    if not cleaned or len(cleaned) > 60:
        return False
    lowered = cleaned.lower()
    banned_fragments = ["@", "http", "www.", "linkedin", "contact", "email", "phone", "skill", "experience"]
    if any(fragment in lowered for fragment in banned_fragments):
        return False
    words = cleaned.replace(".", " ").split()
    if not 2 <= len(words) <= 4:
        return False
    return all(word[:1].isalpha() for word in words)


def _looks_like_contact_line(line: str) -> bool:
    """Estimate whether a line is mostly contact metadata rather than useful summary text."""
    lowered = line.lower()
    return any(fragment in lowered for fragment in ["@", "linkedin", "www.", "http", "contact", "phone"])


def _clean_list(value) -> list[str]:
    """Normalize list-like values into a clean list of strings."""
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _to_float(value) -> float | None:
    """Safely convert incoming numeric values into floats."""
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
