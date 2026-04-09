from typing import Any


def api_response(success: bool, data: Any, message: str, error: str | None = None) -> dict[str, Any]:
    """Return API responses in the required common format."""
    return {"success": success, "data": data, "message": message, "error": error}
