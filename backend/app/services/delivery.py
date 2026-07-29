import uuid
from datetime import datetime, timezone
from typing import Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ValidationException
from app.models.delivery import Delivery, DeliveryStatus
from app.repositories.delivery import DeliveryRepository
from app.schemas.delivery import DeliveryCreate, DeliveryUpdate
from app.services.base import BaseService


class DeliveryService(BaseService[Delivery, DeliveryCreate, DeliveryUpdate]):
    """
    Business logic service for Delivery operations, state transitions, and scheduling.
    """
    def __init__(self, session: AsyncSession) -> None:
        self.delivery_repo = DeliveryRepository(session=session)
        super().__init__(repository=self.delivery_repo)

    # pyrefly: ignore [bad-override]
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

    async def update(self, id: uuid.UUID, obj_in: Union[DeliveryUpdate, dict]) -> Delivery:
        delivery = await self.get_by_id(id)
        
        status_val = getattr(obj_in, "status", None) if hasattr(obj_in, "status") else obj_in.get("status") if isinstance(obj_in, dict) else None
        if status_val == DeliveryStatus.DELIVERED or status_val == "DELIVERED":
            delivery.delivered_at = datetime.now(timezone.utc)
            
        return await self.delivery_repo.update(delivery, obj_in=obj_in)

    async def schedule_delivery(self, delivery_id: uuid.UUID, scheduled_date: datetime) -> Delivery:
        delivery = await self.get_by_id(delivery_id)
        delivery.scheduled_date = scheduled_date
        return await self.delivery_repo.update(delivery, obj_in={})
