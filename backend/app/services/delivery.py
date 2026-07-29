import uuid
from datetime import datetime, timezone
import random
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ValidationException
from app.models.delivery import Delivery, DeliveryStatus
from app.repositories.delivery import DeliveryRepository
from app.schemas.delivery import DeliveryCreate, DeliveryUpdate
from app.services.base import BaseService


class DeliveryService(BaseService[Delivery, DeliveryCreate, DeliveryUpdate]):
    """
    Business logic service for Delivery operations and scheduling.
    """
    def __init__(self, session: AsyncSession) -> None:
        self.delivery_repo = DeliveryRepository(session=session)
        super().__init__(repository=self.delivery_repo)

    async def create(self, obj_in: DeliveryCreate) -> Delivery:
        if not obj_in.tracking_number:
            obj_in.tracking_number = f"TRK-{uuid.uuid4().hex[:8].upper()}"
        else:
            existing = await self.delivery_repo.get_by_tracking(obj_in.tracking_number)
            if existing:
                raise ValidationException(
                    message=f"Delivery with tracking number '{obj_in.tracking_number}' already exists."
                )
        return await super().create(obj_in)

    async def schedule_delivery(self, delivery_id: uuid.UUID, scheduled_date: datetime) -> Delivery:
        delivery = await self.get_by_id(delivery_id)
        delivery.scheduled_date = scheduled_date
        return await self.delivery_repo.update(delivery, obj_in={})
