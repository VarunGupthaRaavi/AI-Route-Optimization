from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ValidationException
from app.models.vehicle import Vehicle
from app.repositories.vehicle import VehicleRepository
from app.schemas.vehicle import VehicleCreate, VehicleUpdate
from app.services.base import BaseService


class VehicleService(BaseService[Vehicle, VehicleCreate, VehicleUpdate]):
    """
    Business logic service for Vehicle operations.
    """
    def __init__(self, session: AsyncSession) -> None:
        self.vehicle_repo = VehicleRepository(session=session)
        super().__init__(repository=self.vehicle_repo)

    async def create(self, obj_in: VehicleCreate) -> Vehicle:
        existing = await self.vehicle_repo.get_by_license_plate(obj_in.license_plate)
        if existing:
            raise ValidationException(
                message=f"Vehicle with license plate '{obj_in.license_plate}' already exists."
            )
        obj_in.license_plate = obj_in.license_plate.upper().strip()
        return await super().create(obj_in)
