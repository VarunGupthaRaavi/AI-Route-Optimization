import uuid
from typing import List
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db_session
from app.models.user import User
from app.schemas.base import ResponseModel
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.services.notification import NotificationService

router = APIRouter()


@router.get(
    "",
    response_model=ResponseModel[List[NotificationResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get authenticated user's notification feed"
)
async def list_notifications(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[List[NotificationResponse]]:
    request_id = getattr(request.state, "request_id", None)
    service = NotificationService(session=db)
    notifs = await service.get_user_notifications(current_user.id)
    items = [NotificationResponse.model_validate(n) for n in notifs]
    return ResponseModel(success=True, data=items, message="Notifications retrieved successfully.", request_id=request_id)


@router.post(
    "",
    response_model=ResponseModel[NotificationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new notification"
)
async def create_notification(
    obj_in: NotificationCreate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[NotificationResponse]:
    request_id = getattr(request.state, "request_id", None)
    service = NotificationService(session=db)
    notif = await service.create(obj_in)
    return ResponseModel(success=True, data=NotificationResponse.model_validate(notif), message="Notification created successfully.", request_id=request_id)


@router.put(
    "/{notification_id}/read",
    response_model=ResponseModel[NotificationResponse],
    status_code=status.HTTP_200_OK,
    summary="Mark a notification as read"
)
async def mark_notification_read(
    notification_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[NotificationResponse]:
    request_id = getattr(request.state, "request_id", None)
    service = NotificationService(session=db)
    notif = await service.mark_as_read(notification_id)
    return ResponseModel(success=True, data=NotificationResponse.model_validate(notif), message="Notification marked as read.", request_id=request_id)


@router.put(
    "/read-all",
    response_model=ResponseModel[int],
    status_code=status.HTTP_200_OK,
    summary="Mark all user notifications as read"
)
async def mark_all_notifications_read(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[int]:
    request_id = getattr(request.state, "request_id", None)
    service = NotificationService(session=db)
    count = await service.mark_all_as_read(current_user.id)
    return ResponseModel(success=True, data=count, message=f"{count} notifications marked as read.", request_id=request_id)
