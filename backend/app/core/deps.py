"""FastAPI dependencies — JWT admin + public API-key tenant."""

from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.origins import origin_allowed
from app.core.rate_limit import check_rate_limit
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models import Tenant, User

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = UUID(payload["sub"])
    except (ValueError, KeyError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from None

    result = await db.execute(
        select(User).options(selectinload(User.tenant)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_tenant_from_api_key(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_api_key: str | None = Header(default=None, alias="X-Api-Key"),
    origin: str | None = Header(default=None),
) -> Tenant:
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Api-Key header",
        )

    result = await db.execute(select(Tenant).where(Tenant.api_key == x_api_key))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    # Prefer Origin; fall back to Referer scheme+host
    check_origin = origin
    if not check_origin:
        referer = request.headers.get("referer")
        if referer:
            from urllib.parse import urlparse

            parsed = urlparse(referer)
            if parsed.scheme and parsed.netloc:
                check_origin = f"{parsed.scheme}://{parsed.netloc}"

    if not origin_allowed(check_origin, list(tenant.allowed_origins or [])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Origin not allowed for this tenant",
        )

    client_ip = request.client.host if request.client else "unknown"
    allowed, retry_after = await check_rate_limit(
        api_key=tenant.api_key,
        ip=client_ip,
        limit_rpm=tenant.rate_limit_rpm,
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(retry_after)},
        )

    return tenant
