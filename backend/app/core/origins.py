"""Origin allowlist helpers for widget requests."""

from __future__ import annotations

from urllib.parse import urlparse


def normalize_origin(origin: str | None) -> str | None:
    if origin is None:
        return None
    origin = origin.strip()
    if not origin or origin.lower() == "null":
        return "null"
    parsed = urlparse(origin)
    if not parsed.scheme or not parsed.netloc:
        return origin.rstrip("/")
    return f"{parsed.scheme}://{parsed.netloc}"


def origin_allowed(origin: str | None, allowed: list[str] | None) -> bool:
    """
    If allowed list is empty → allow (dev convenience).
    Otherwise origin must match an entry exactly (normalized).
    """
    allowed = allowed or []
    if not allowed:
        return True
    normalized_allowed = {normalize_origin(a) for a in allowed if a}
    current = normalize_origin(origin)
    if current is None:
        return False
    return current in normalized_allowed
