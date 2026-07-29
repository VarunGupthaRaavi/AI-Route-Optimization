from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.driver import Driver
from app.repositories.base import BaseRepository
from app.schemas.driver import DriverCreate, DriverUpdate


class DriverRepository(BaseRepository[Driver, DriverCreate, DriverUpdate]):
    """
    Data repository for Driver entities.
    """
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Driver, session=session)

    async def get_by_license(self, license_num: str) -> Optional[Driver]:
        stmt = select(Driver).where(
            Driver.license_number == license_num.upper().strip(),
            Driver.is_deleted == False
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()
