import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.delivery import Delivery, DeliveryStatus
from app.repositories.base import BaseRepository
from app.schemas.delivery import DeliveryCreate, DeliveryUpdate


class DeliveryRepository(BaseRepository[Delivery, DeliveryCreate, DeliveryUpdate]):
    """
    Data repository for Delivery entities.
    """
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Delivery, session=session)

    async def get_by_tracking(self, tracking_number: str) -> Optional[Delivery]:
        stmt = select(Delivery).where(
            Delivery.tracking_number == tracking_number.strip(),
            Delivery.is_deleted == False
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_pending_deliveries(self) -> List[Delivery]:
        stmt = select(Delivery).where(
            Delivery.status == DeliveryStatus.PENDING,
            Delivery.is_deleted == False
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
