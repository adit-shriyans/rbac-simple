from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session, require_roles
from app.models.enums import UserRole
from app.schemas.summary import DashboardSummary
from app.services.dashboard import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummary,
    dependencies=[Depends(require_roles(UserRole.ANALYST, UserRole.ADMIN))],
)
async def get_dashboard_summary(
    start_date: date | None = None,
    end_date: date | None = None,
    session: AsyncSession = Depends(db_session),
):
    return await DashboardService(session).get_summary(
        start_date=start_date, end_date=end_date
    )
