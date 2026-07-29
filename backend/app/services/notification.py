import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification, NotificationType
from app.repositories.notification import NotificationRepository
from app.schemas.notification import NotificationCreate
from app.services.base import BaseService


class NotificationService(BaseService[Notification, NotificationCreate, NotificationCreate]):
    """
    Business logic service for Notification alert management.
    """
    def __init__(self, session: AsyncSession) -> None:
        self.notif_repo = NotificationRepository(session=session)
        super().__init__(repository=self.notif_repo)

    async def get_user_notifications(self, user_id: uuid.UUID) -> List[Notification]:
        return await self.notif_repo.get_user_notifications(user_id)

    async def mark_as_read(self, notification_id: uuid.UUID) -> Notification:
        notif = await self.get_by_id(notification_id)
        notif.is_read = True
        return await self.notif_repo.update(notif, obj_in={})

    async def mark_all_as_read(self, user_id: uuid.UUID) -> int:
        return await self.notif_repo.mark_all_as_read(user_id)
