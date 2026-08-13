"""Public widget config — branding for embed (X-Api-Key)."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.deps import get_tenant_from_api_key
from app.models import Tenant

router = APIRouter(prefix="/widget", tags=["widget"])


class WidgetConfigOut(BaseModel):
    bot_name: str
    primary_color: str
    welcome_message: str
    starter_questions: list[str]
    business_name: str


@router.get("/config", response_model=WidgetConfigOut)
async def widget_config(tenant: Tenant = Depends(get_tenant_from_api_key)) -> WidgetConfigOut:
    starters = tenant.starter_questions or []
    if not isinstance(starters, list):
        starters = []
    return WidgetConfigOut(
        bot_name=tenant.bot_name,
        primary_color=tenant.primary_color,
        welcome_message=tenant.welcome_message,
        starter_questions=[str(s) for s in starters],
        business_name=tenant.name,
    )
