import uuid
from typing import List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification
from app.repositories.base import BaseRepository
from app.schemas.notification import NotificationCreate


class NotificationRepository(BaseRepository[Notification, NotificationCreate, NotificationCreate]):
    """
    Data repository for Notification entities.
    """
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Notification, session=session)

    async def get_user_notifications(self, user_id: uuid.UUID) -> List[Notification]:
        stmt = select(Notification).where(
            Notification.user_id == user_id,
            Notification.is_deleted == False
        ).order_by(Notification.created_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def mark_all_as_read(self, user_id: uuid.UUID) -> int:
        stmt = update(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).values(is_read=True)
        res = await self.session.execute(stmt)
        return res.rowcount
