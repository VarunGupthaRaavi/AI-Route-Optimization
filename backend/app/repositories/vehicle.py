from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.vehicle import Vehicle, VehicleStatus
from app.repositories.base import BaseRepository
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


class VehicleRepository(BaseRepository[Vehicle, VehicleCreate, VehicleUpdate]):
    """
    Data repository for Vehicle entities.
    """
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Vehicle, session=session)

    async def get_by_license_plate(self, plate: str) -> Optional[Vehicle]:
        stmt = select(Vehicle).where(
            Vehicle.license_plate == plate.upper().strip(),
            Vehicle.is_deleted == False
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()
