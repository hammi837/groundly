"""Seed Riverside demo — runnable inside Railway container: python seed_demo.py"""

from __future__ import annotations

import asyncio
import secrets
import sys
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.security import hash_password
from app.models import Chunk, Document, Tenant, User
from app.services.ingest import process_document_job

DEMO_ORIGINS = [
    "https://groundly-production.up.railway.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
    "null",
]

FAQS: list[tuple[str, str, str]] = [
    (
        "Office hours",
        "What are your office hours?",
        "Monday to Friday 8:00 AM to 5:00 PM. Saturday 9:00 AM to 1:00 PM. Closed Sunday.",
    ),
    (
        "Insurance plans",
        "Which insurance plans do you accept?",
        "We accept Delta Dental PPO, Cigna, MetLife, and most major PPO plans. Bring your insurance card to your first visit.",
    ),
    (
        "Delta Dental",
        "Do you accept Delta Dental?",
        "Yes. Riverside Dental accepts Delta Dental PPO plans.",
    ),
    (
        "Appointments",
        "How do I book an appointment?",
        "Call our phone number (555) 010-2200 or book online. New patients should arrive 15 minutes early. Same-day emergency slots are held each morning.",
    ),
    (
        "Parking",
        "Where can I park?",
        "Free parking is available behind the clinic on Maple Street.",
    ),
    (
        "Location",
        "Where are you located?",
        "Our address is 220 Maple Street, Suite 100, Riverside. Riverside Dental Group is located there.",
    ),
    (
        "Whitening",
        "Do you offer teeth whitening?",
        "Yes. We offer in-office professional whitening. Ask at your next cleaning visit.",
    ),
    (
        "Children",
        "Do you see children?",
        "Yes. We welcome families and see children age 3 and older for routine care.",
    ),
    (
        "Sedation",
        "Do you offer sedation dentistry?",
        "Yes. We offer nitrous oxide (laughing gas) for anxious patients. Ask when you book.",
    ),
]


def _merge_origins(existing: list[str] | None) -> list[str]:
    out: list[str] = []
    for o in (existing or []) + DEMO_ORIGINS:
        if o not in out:
            out.append(o)
    return out


async def seed(*, force_faqs: bool = False) -> None:
    get_settings.cache_clear()
    from app.core.config import settings as cfg

    engine = create_async_engine(cfg.database_url, echo=False)
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    email = cfg.seed_admin_email.lower()
    password = cfg.seed_admin_password

    async with Session() as db:
        existing_user = (
            await db.execute(select(User).where(User.email == email))
        ).scalar_one_or_none()

        if existing_user:
            tenant = (
                await db.execute(select(Tenant).where(Tenant.id == existing_user.tenant_id))
            ).scalar_one()
            tenant.allowed_origins = _merge_origins(tenant.allowed_origins)
            await db.commit()
            print(f"Tenant already exists: {tenant.name}")
            print(f"  admin:   {email}")
            print(f"  password:{password}")
            print(f"  api_key: {tenant.api_key}")
        else:
            tenant = Tenant(
                name="Riverside Dental Group",
                api_key=secrets.token_urlsafe(32),
                bot_name="Riverside Assistant",
                primary_color="#0F766E",
                welcome_message=(
                    "Hi! I'm the Riverside Dental assistant. Ask about hours, insurance, or appointments."
                ),
                starter_questions=[
                    "What are your office hours?",
                    "Do you accept Delta Dental?",
                    "How do I book an appointment?",
                ],
                allowed_origins=list(DEMO_ORIGINS),
                rate_limit_rpm=60,
            )
            user = User(
                tenant=tenant,
                email=email,
                hashed_password=hash_password(password),
            )
            db.add(user)
            await db.commit()
            await db.refresh(tenant)
            print("Seeded Riverside Dental demo tenant")
            print(f"  tenant_id: {tenant.id}")
            print(f"  admin:     {email}")
            print(f"  password:  {password}")
            print(f"  api_key:   {tenant.api_key}")

        docs = (
            await db.execute(select(Document).where(Document.tenant_id == tenant.id))
        ).scalars().all()

        if docs and not force_faqs:
            print(f"FAQs already present ({len(docs)} docs). Use --force-faqs to re-ingest.")
        else:
            if force_faqs and docs:
                print("Removing existing docs for --force-faqs…")
                await db.execute(delete(Chunk).where(Chunk.tenant_id == tenant.id))
                await db.execute(delete(Document).where(Document.tenant_id == tenant.id))
                await db.commit()

            print("Ingesting demo FAQs…")
            tenant_id = tenant.id
            for title, question, answer in FAQS:
                faq_text = f"Question: {question}\n\nAnswer: {answer}"
                doc_id = uuid4()
                db.add(
                    Document(
                        id=doc_id,
                        tenant_id=tenant_id,
                        source_type="faq",
                        source_name=title,
                        status="processing",
                        bytes=len(faq_text.encode("utf-8")),
                        chunk_count=0,
                    )
                )
                await db.commit()
                await process_document_job(str(doc_id), faq_text=faq_text)
                refreshed = (
                    await db.execute(select(Document).where(Document.id == doc_id))
                ).scalar_one()
                print(f"  [{refreshed.status}] {title} chunks={refreshed.chunk_count}")

        print("\nDone. Save the api_key above for the widget demo.")

    await engine.dispose()


if __name__ == "__main__":
    force = "--force-faqs" in sys.argv
    asyncio.run(seed(force_faqs=force))
