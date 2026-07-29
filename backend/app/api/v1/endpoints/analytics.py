from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db_session
from app.models.user import User
from app.schemas.analytics import AnalyticsSummary
from app.schemas.base import ResponseModel
from app.services.analytics import AnalyticsService

router = APIRouter()


@router.get(
    "/dashboard",
    response_model=ResponseModel[AnalyticsSummary],
    status_code=status.HTTP_200_OK,
    summary="Get executive dashboard analytics & KPI metrics"
)
async def get_dashboard_analytics(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[AnalyticsSummary]:
    request_id = getattr(request.state, "request_id", None)
    service = AnalyticsService(session=db)
    summary = await service.get_dashboard_summary()
    return ResponseModel(success=True, data=summary, message="Analytics summary generated successfully.", request_id=request_id)
