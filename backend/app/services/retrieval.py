"""Hybrid retrieval — full-text + in-Python cosine (no pgvector required)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Chunk
from app.services.embeddings import embed_texts


@dataclass
class RetrievedChunk:
    id: UUID
    content: str
    metadata: dict
    score: float
    source_name: str


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b, strict=True):
        dot += x * y
        na += x * x
        nb += y * y
    if na <= 0 or nb <= 0:
        return 0.0
    return dot / math.sqrt(na * nb)


async def hybrid_search(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    query: str,
    top_k: int | None = None,
) -> list[RetrievedChunk]:
    top_k = top_k or settings.retrieval_top_k
    query = query.strip()
    if not query:
        return []

    vectors, _ = await embed_texts([query])
    query_vec = vectors[0]

    # Load tenant chunks (fine for portfolio / SMB knowledge bases)
    rows = (
        await db.execute(select(Chunk).where(Chunk.tenant_id == tenant_id))
    ).scalars().all()

    vec_ranked: list[tuple[Chunk, float]] = []
    for chunk in rows:
        emb = list(chunk.embedding or [])
        score = _cosine(query_vec, emb)
        vec_ranked.append((chunk, score))
    vec_ranked.sort(key=lambda t: t[1], reverse=True)
    vec_top = vec_ranked[:top_k]

    fts_sql = text(
        """
        SELECT id
        FROM chunks
        WHERE tenant_id = CAST(:tenant_id AS uuid)
          AND content_tsv @@ plainto_tsquery('english', :q)
        ORDER BY ts_rank_cd(content_tsv, plainto_tsquery('english', :q)) DESC
        LIMIT :lim
        """
    )
    fts_ids = [
        row[0] if not isinstance(row, dict) else row["id"]
        for row in (
            await db.execute(
                fts_sql,
                {"q": query, "tenant_id": str(tenant_id), "lim": top_k},
            )
        ).all()
    ]
    # normalize UUID types
    fts_ids = [i if isinstance(i, UUID) else UUID(str(i)) for i in fts_ids]

    rrf_k = settings.rrf_k
    scores: dict[UUID, float] = {}
    payloads: dict[UUID, Chunk] = {c.id: c for c, _ in vec_top}
    for c, _ in vec_top:
        payloads[c.id] = c
    for c in rows:
        if c.id in fts_ids:
            payloads[c.id] = c

    for rank, (chunk, _) in enumerate(vec_top):
        scores[chunk.id] = scores.get(chunk.id, 0.0) + 1.0 / (rrf_k + rank + 1)

    for rank, cid in enumerate(fts_ids):
        scores[cid] = scores.get(cid, 0.0) + 1.0 / (rrf_k + rank + 1)

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
    results: list[RetrievedChunk] = []
    for cid, score in ranked:
        chunk = payloads.get(cid)
        if chunk is None:
            continue
        meta = chunk.metadata_ if isinstance(chunk.metadata_, dict) else {}
        results.append(
            RetrievedChunk(
                id=cid,
                content=chunk.content,
                metadata=meta,
                score=float(score),
                source_name=str(meta.get("source_name") or "document"),
            )
        )
    return results
