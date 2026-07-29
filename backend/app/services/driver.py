from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ValidationException
from app.models.driver import Driver
from app.repositories.driver import DriverRepository
from app.schemas.driver import DriverCreate, DriverUpdate
from app.services.base import BaseService


class DriverService(BaseService[Driver, DriverCreate, DriverUpdate]):
    """
    Business logic service for Driver operations.
    """
    def __init__(self, session: AsyncSession) -> None:
        self.driver_repo = DriverRepository(session=session)
        super().__init__(repository=self.driver_repo)

    async def create(self, obj_in: DriverCreate) -> Driver:
        existing = await self.driver_repo.get_by_license(obj_in.license_number)
        if existing:
            raise ValidationException(
                message=f"Driver with license number '{obj_in.license_number}' already exists."
            )
        obj_in.license_number = obj_in.license_number.upper().strip()
        return await super().create(obj_in)
