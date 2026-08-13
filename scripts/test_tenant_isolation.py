"""Tenant isolation tests — schema + hybrid retrieval cross-leak checks (Phase 3)."""

from __future__ import annotations

import asyncio
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from sqlalchemy import func, select  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models import Chunk, Document, Tenant, User  # noqa: E402
from app.services.embeddings import embed_texts  # noqa: E402
from app.services.retrieval import hybrid_search  # noqa: E402


async def main() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as db:
        a = Tenant(
            name="Isolation A",
            api_key=secrets.token_urlsafe(24),
            starter_questions=[],
            allowed_origins=["http://localhost:5173"],
        )
        b = Tenant(
            name="Isolation B",
            api_key=secrets.token_urlsafe(24),
            starter_questions=[],
            allowed_origins=["http://localhost:5173"],
        )
        db.add_all([a, b])
        await db.flush()

        doc_a = Document(
            tenant_id=a.id,
            source_type="faq",
            source_name="A-secret-handbook",
            status="ready",
            chunk_count=1,
        )
        doc_b = Document(
            tenant_id=b.id,
            source_type="faq",
            source_name="B-secret-handbook",
            status="ready",
            chunk_count=1,
        )
        db.add_all(
            [
                User(
                    tenant_id=a.id,
                    email=f"a-{a.id.hex[:8]}@iso.test",
                    hashed_password=hash_password("test-pass-1"),
                ),
                User(
                    tenant_id=b.id,
                    email=f"b-{b.id.hex[:8]}@iso.test",
                    hashed_password=hash_password("test-pass-1"),
                ),
                doc_a,
                doc_b,
            ]
        )
        await db.flush()

        text_a = "Tenant A exclusive policy: purple zebra dental floss discount code ALPHA-ONLY."
        text_b = "Tenant B exclusive policy: golden mango whitening kit code BRAVO-ONLY."
        emb_a, _ = await embed_texts([text_a])
        emb_b, _ = await embed_texts([text_b])

        chunk_a = Chunk(
            document_id=doc_a.id,
            tenant_id=a.id,
            content=text_a,
            embedding=emb_a[0],
            metadata_={"source_name": doc_a.source_name, "page": 1},
        )
        chunk_b = Chunk(
            document_id=doc_b.id,
            tenant_id=b.id,
            content=text_b,
            embedding=emb_b[0],
            metadata_={"source_name": doc_b.source_name, "page": 1},
        )
        db.add_all([chunk_a, chunk_b])
        await db.commit()

        # Schema-level checks
        a_docs = (
            await db.execute(select(func.count()).select_from(Document).where(Document.tenant_id == a.id))
        ).scalar_one()
        leaked_docs = (
            await db.execute(
                select(func.count())
                .select_from(Document)
                .where(Document.tenant_id == a.id, Document.source_name == "B-secret-handbook")
            )
        ).scalar_one()

        # Retrieval must not return the other tenant's secret phrase
        hits_a = await hybrid_search(
            db, tenant_id=a.id, query="golden mango whitening kit BRAVO-ONLY", top_k=5
        )
        hits_b = await hybrid_search(
            db, tenant_id=b.id, query="purple zebra dental floss ALPHA-ONLY", top_k=5
        )

        leak_a = any("BRAVO-ONLY" in h.content or "B-secret" in h.source_name for h in hits_a)
        leak_b = any("ALPHA-ONLY" in h.content or "A-secret" in h.source_name for h in hits_b)

        # Positive control: A finds its own content
        own_a = await hybrid_search(db, tenant_id=a.id, query="purple zebra ALPHA-ONLY", top_k=3)
        found_own = any("ALPHA-ONLY" in h.content for h in own_a)

        print(f"tenant_a={a.id} docs={a_docs}")
        print(f"cross_doc_leak={leaked_docs}")
        print(f"retrieval_leak_a_sees_b={leak_a} hits={len(hits_a)}")
        print(f"retrieval_leak_b_sees_a={leak_b} hits={len(hits_b)}")
        print(f"retrieval_finds_own={found_own}")

        ok = (
            a_docs == 1
            and leaked_docs == 0
            and not leak_a
            and not leak_b
            and found_own
            and a.id != b.id
        )

        await db.delete(a)
        await db.delete(b)
        await db.commit()

    await engine.dispose()

    if not ok:
        raise SystemExit("FAIL: tenant isolation check failed")
    print("PASS: schema + hybrid retrieval tenant isolation (Phase 3).")


if __name__ == "__main__":
    asyncio.run(main())
