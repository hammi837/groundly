"""Tenant settings (JWT) — branding, origins, embed snippet, API key."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models import Tenant, User
from app.schemas.settings import SettingsOut, SettingsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


def _mask_key(key: str) -> str:
    if len(key) <= 8:
        return "••••••••"
    return f"{key[:4]}…{key[-4:]}"


def _embed_snippet(api_key: str) -> str:
    # Placeholder host; admin can change api-base in production
    base = "https://YOUR_API_HOST"
    return (
        f'<script src="https://YOUR_CDN/widget.js"\n'
        f'  data-api-base="{base}"\n'
        f'  data-api-key="{api_key}"\n'
        f'  async></script>'
    )


def _to_out(tenant: Tenant, *, reveal: bool = False) -> SettingsOut:
    starters = tenant.starter_questions if isinstance(tenant.starter_questions, list) else []
    origins = list(tenant.allowed_origins or [])
    return SettingsOut(
        business_name=tenant.name,
        bot_name=tenant.bot_name,
        primary_color=tenant.primary_color,
        welcome_message=tenant.welcome_message,
        starter_questions=[str(s) for s in starters],
        allowed_origins=origins,
        rate_limit_rpm=tenant.rate_limit_rpm,
        webhook_url=tenant.webhook_url,
        api_key_masked=_mask_key(tenant.api_key),
        api_key=tenant.api_key if reveal else None,
        embed_snippet=_embed_snippet(tenant.api_key),
    )


@router.get("", response_model=SettingsOut)
async def get_settings(
    reveal_key: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SettingsOut:
    result = await db.execute(select(Tenant).where(Tenant.id == current_user.tenant_id))
    tenant = result.scalar_one()
    return _to_out(tenant, reveal=reveal_key)


@router.patch("", response_model=SettingsOut)
async def patch_settings(
    body: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SettingsOut:
    result = await db.execute(select(Tenant).where(Tenant.id == current_user.tenant_id))
    tenant = result.scalar_one()

    data = body.model_dump(exclude_unset=True)
    if "webhook_url" in data and data["webhook_url"] == "":
        data["webhook_url"] = None
    if "primary_color" in data and data["primary_color"]:
        color = data["primary_color"]
        if not color.startswith("#") or len(color) not in (4, 7):
            raise HTTPException(status_code=400, detail="primary_color must be #RGB or #RRGGBB")

    for key, value in data.items():
        setattr(tenant, key, value)

    await db.commit()
    await db.refresh(tenant)
    return _to_out(tenant)
