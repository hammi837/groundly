"""Run Riverside Dental golden eval — prints honest pass rate for case studies."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
EVAL_PATH = ROOT / "evals" / "riverside_dental.json"
sys.path.insert(0, str(BACKEND))

from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.models import Tenant  # noqa: E402
from app.services.llm import generate_answer  # noqa: E402
from app.services.retrieval import hybrid_search  # noqa: E402
from app.core.config import settings as app_settings  # noqa: E402


def load_cases() -> list[dict]:
    return json.loads(EVAL_PATH.read_text(encoding="utf-8"))


async def eval_one(db: AsyncSession, tenant: Tenant, case: dict) -> dict:
    question = case["question"]
    expect = case["expect"]  # answer | fallback

    chunks = await hybrid_search(db, tenant_id=tenant.id, query=question)
    top_score = chunks[0].score if chunks else 0.0
    weak = (not chunks) or top_score < app_settings.relevance_threshold

    if weak:
        was_fallback = True
        answer = "(threshold fallback — skipped LLM)"
    else:
        result = await generate_answer(
            business_name=tenant.name,
            question=question,
            chunks=chunks,
        )
        was_fallback = result.was_fallback
        answer = result.answer

    predicted = "fallback" if was_fallback else "answer"
    passed = predicted == expect
    return {
        "id": case["id"],
        "expect": expect,
        "predicted": predicted,
        "pass": passed,
        "top_score": round(top_score, 4),
        "question": question,
        "answer_preview": answer[:160].replace("\n", " "),
    }


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tenant-name", default="Riverside Dental Group")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    get_settings.cache_clear()
    from app.core.config import settings

    cases = load_cases()
    if not cases:
        raise SystemExit("evals/riverside_dental.json is empty")

    engine = create_async_engine(settings.database_url, echo=False)
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as db:
        tenant = (
            await db.execute(select(Tenant).where(Tenant.name == args.tenant_name))
        ).scalar_one_or_none()
        if tenant is None:
            await engine.dispose()
            raise SystemExit("Tenant not found — run: python scripts/seed_riverside.py")

        results = []
        for case in cases:
            row = await eval_one(db, tenant, case)
            results.append(row)
            mark = "PASS" if row["pass"] else "FAIL"
            if args.verbose or not row["pass"]:
                print(f"[{mark}] {row['id']} expect={row['expect']} got={row['predicted']} :: {row['question']}")

    await engine.dispose()

    passed = sum(1 for r in results if r["pass"])
    total = len(results)
    rate = (passed / total) * 100 if total else 0.0
    answer_cases = [r for r in results if r["expect"] == "answer"]
    fallback_cases = [r for r in results if r["expect"] == "fallback"]
    answer_pass = sum(1 for r in answer_cases if r["pass"])
    fallback_pass = sum(1 for r in fallback_cases if r["pass"])

    print("\n=== Groundly golden eval (Riverside Dental) ===")
    print(f"Total:            {passed}/{total}  ({rate:.1f}%)")
    print(f"Should answer:    {answer_pass}/{len(answer_cases)}")
    print(f"Should fallback:  {fallback_pass}/{len(fallback_cases)}")
    print(f"LLM mode:         {settings.llm_mode}")
    print(f"Embedding mode:   {settings.embedding_mode}")
    print("Claim this pass rate in case studies — not fictional ROI.")

    # non-zero exit if below a soft bar (helpful in CI later)
    if rate < 50:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
