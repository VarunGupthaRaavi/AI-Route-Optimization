import uuid
from datetime import datetime
from typing import Optional
from pydantic import Field
from app.models.notification import NotificationType
from app.schemas.base import BaseSchema


class NotificationBase(BaseSchema):
    user_id: uuid.UUID = Field(..., description="Recipient user ID")
    title: str = Field(..., min_length=2, max_length=255, description="Headline title")
    message: str = Field(..., min_length=2, description="Body message")
    type: NotificationType = Field(default=NotificationType.INFO, description="Notification type")
    is_read: bool = Field(default=False, description="Read flag")


class NotificationCreate(NotificationBase):
    pass


class NotificationResponse(NotificationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
