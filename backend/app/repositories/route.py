import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.route import Route, RouteStop
from app.repositories.base import BaseRepository
from app.schemas.route import RouteCreate, RouteUpdate


class RouteRepository(BaseRepository[Route, RouteCreate, RouteUpdate]):
    """
    Data repository for Route entities and route stops.
    """
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=Route, session=session)

    async def get_route_stops(self, route_id: uuid.UUID) -> List[RouteStop]:
        stmt = select(RouteStop).where(
            RouteStop.route_id == route_id,
            RouteStop.is_deleted == False
        ).order_by(RouteStop.stop_sequence.asc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def create_route_stop(
        self,
        route_id: uuid.UUID,
        delivery_id: uuid.UUID,
        stop_sequence: int
    ) -> RouteStop:
        stop = RouteStop(
            route_id=route_id,
            delivery_id=delivery_id,
            stop_sequence=stop_sequence
        )
        self.session.add(stop)
        await self.session.flush()
        await self.session.refresh(stop)
        return stop
