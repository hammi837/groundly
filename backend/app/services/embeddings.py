"""Embedding providers — OpenAI or deterministic fake vectors for offline dev."""

from __future__ import annotations

import hashlib
import math
import struct

import httpx

from app.core.config import settings


def _fake_embed_one(text: str, dims: int) -> list[float]:
    """Deterministic pseudo-embedding from text hash (not for production quality)."""
    seed = hashlib.sha256(text.encode("utf-8")).digest()
    values: list[float] = []
    counter = 0
    while len(values) < dims:
        block = hashlib.sha256(seed + counter.to_bytes(4, "little")).digest()
        for i in range(0, len(block), 4):
            if len(values) >= dims:
                break
            (n,) = struct.unpack_from("!I", block, i)
            values.append((n / 0xFFFFFFFF) * 2.0 - 1.0)
        counter += 1
    # L2 normalize
    norm = math.sqrt(sum(v * v for v in values)) or 1.0
    return [v / norm for v in values]


async def embed_texts(texts: list[str]) -> tuple[list[list[float]], int]:
    """
    Returns (embeddings, estimated_or_actual_token_usage).
    """
    if not texts:
        return [], 0

    mode = settings.embedding_mode.lower().strip()
    if mode == "fake":
        vectors = [_fake_embed_one(t, settings.embedding_dims) for t in texts]
        # rough token estimate
        tokens = sum(max(1, len(t) // 4) for t in texts)
        return vectors, tokens

    if mode != "openai":
        raise ValueError(f"Unknown embedding_mode: {settings.embedding_mode}")

    if not settings.openai_api_key:
        raise ValueError(
            "OPENAI_API_KEY is required when EMBEDDING_MODE=openai. "
            "Set EMBEDDING_MODE=fake for offline ingest."
        )

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/embeddings",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.embedding_model,
                "input": texts,
            },
        )
        response.raise_for_status()
        payload = response.json()

    # Ensure order by index
    data = sorted(payload["data"], key=lambda row: row["index"])
    vectors = [row["embedding"] for row in data]
    tokens = int(payload.get("usage", {}).get("total_tokens") or 0)
    return vectors, tokens
