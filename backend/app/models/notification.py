import uuid
from enum import Enum
from typing import Optional
from sqlalchemy import Boolean, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class NotificationType(str, Enum):
    """
    Notification severity and intent classification.
    """
    INFO = "INFO"
    WARNING = "WARNING"
    SUCCESS = "SUCCESS"
    ALERT = "ALERT"


class Notification(BaseModel):
    """
    SQLAlchemy 2.0 Notification Entity Model.
    Stores real-time system alerts, dispatch notifications, and warnings for users.
    """
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Target recipient user ID"
    )
    title: Mapped[str] = mapped_column(
        String(255), nullable=False, doc="Notification headline title"
    )
    message: Mapped[str] = mapped_column(
        Text, nullable=False, doc="Notification body text"
    )
    type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType, name="notificationtype", native_enum=True),
        default=NotificationType.INFO,
        nullable=False,
        index=True,
        doc="Notification classification tier"
    )
    is_read: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True, doc="Read status indicator"
    )

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, user_id={self.user_id}, title='{self.title}', read={self.is_read})>"
