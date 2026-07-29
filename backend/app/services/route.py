import math
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundException, ValidationException
from app.models.delivery import DeliveryStatus
from app.models.driver import DriverStatus
from app.models.route import Route, RouteStatus
from app.models.vehicle import VehicleStatus
from app.repositories.delivery import DeliveryRepository
from app.repositories.driver import DriverRepository
from app.repositories.route import RouteRepository
from app.repositories.vehicle import VehicleRepository
from app.schemas.route import RouteCreate, RouteOptimizeRequest, RouteResponse, RouteStopResponse, RouteUpdate
from app.services.base import BaseService


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates great-circle distance between two geographic coordinates in kilometers.
    """
    R = 6371.0  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


class RouteService(BaseService[Route, RouteCreate, RouteUpdate]):
    """
    Business logic service for Logistics Route Optimization & Driver Allocation.
    """
    def __init__(self, session: AsyncSession) -> None:
        self.route_repo = RouteRepository(session=session)
        self.delivery_repo = DeliveryRepository(session=session)
        self.driver_repo = DriverRepository(session=session)
        self.vehicle_repo = VehicleRepository(session=session)
        super().__init__(repository=self.route_repo)

    async def get_route_details(self, route_id: uuid.UUID) -> RouteResponse:
        route = await self.get_by_id(route_id)
        stops = await self.route_repo.get_route_stops(route_id)
        stop_responses = [RouteStopResponse.model_validate(s) for s in stops]
        
        response = RouteResponse.model_validate(route)
        response.stops = stop_responses
        return response

    async def optimize_route(self, req: RouteOptimizeRequest) -> RouteResponse:
        """
        AI Logistics Route Optimization algorithm using Nearest-Neighbor TSP heuristic.
        Orders pending deliveries into an optimized sequence minimizing travel distance.
        """
        # 1. Fetch requested deliveries
        deliveries = []
        for del_id in req.delivery_ids:
            deliv = await self.delivery_repo.get_by_id(del_id)
            if deliv:
                deliveries.append(deliv)

        if not deliveries:
            raise ValidationException("No valid pending deliveries provided for route optimization.")

        # 2. Nearest Neighbor TSP heuristic optimization
        unvisited = deliveries.copy()
        current_lat = unvisited[0].pickup_lat
        current_lng = unvisited[0].pickup_lng
        
        optimized_order = []
        total_distance = 0.0

        while unvisited:
            nearest = min(
                unvisited,
                key=lambda d: haversine_distance_km(current_lat, current_lng, d.delivery_lat, d.delivery_lng)
            )
            dist = haversine_distance_km(current_lat, current_lng, nearest.delivery_lat, nearest.delivery_lng)
            total_distance += dist
            current_lat, current_lng = nearest.delivery_lat, nearest.delivery_lng
            optimized_order.append(nearest)
            unvisited.remove(nearest)

        # 3. Calculate estimated duration (assuming average 40 km/h city logistics speed + 10 min per stop)
        avg_speed_kmh = 40.0
        travel_hours = total_distance / avg_speed_kmh
        stop_service_mins = len(optimized_order) * 10
        total_duration_mins = int((travel_hours * 60) + stop_service_mins)

        # 4. Create Route Entity
        route_code = f"RT-{uuid.uuid4().hex[:6].upper()}"
        route = await self.route_repo.create({
            "route_code": route_code,
            "vehicle_id": req.vehicle_id,
            "status": RouteStatus.OPTIMIZED,
            "total_distance_km": round(total_distance, 2),
            "estimated_duration_minutes": total_duration_mins,
            "total_deliveries": len(optimized_order)
        })

        # 5. Create RouteStops and update delivery status to ASSIGNED
        stops = []
        now = datetime.now(timezone.utc)
        curr_time = now + timedelta(minutes=15)

        for idx, deliv in enumerate(optimized_order, start=1):
            stop = await self.route_repo.create_route_stop(
                route_id=route.id,
                delivery_id=deliv.id,
                stop_sequence=idx
            )
            stops.append(stop)

            deliv.status = DeliveryStatus.ASSIGNED
            await self.delivery_repo.update(deliv, obj_in={})

        response = RouteResponse.model_validate(route)
        response.stops = [RouteStopResponse.model_validate(s) for s in stops]
        return response

    async def allocate_driver(self, route_id: uuid.UUID, driver_id: uuid.UUID, vehicle_id: Optional[uuid.UUID] = None) -> RouteResponse:
        """
        Allocates a driver and vehicle to an optimized route, updating telemetry and duty statuses.
        """
        route = await self.get_by_id(route_id)
        driver = await self.driver_repo.get_by_id(driver_id)
        if not driver:
            raise EntityNotFoundException("Driver", driver_id)

        target_vehicle_id = vehicle_id or driver.assigned_vehicle_id or route.vehicle_id
        if target_vehicle_id:
            vehicle = await self.vehicle_repo.get_by_id(target_vehicle_id)
            if vehicle:
                vehicle.status = VehicleStatus.IN_TRANSIT
                await self.vehicle_repo.update(vehicle, obj_in={})
                route.vehicle_id = vehicle.id

        driver.status = DriverStatus.ON_ROUTE
        await self.driver_repo.update(driver, obj_in={})

        route.driver_id = driver.id
        route.status = RouteStatus.IN_PROGRESS
        route.started_at = datetime.now(timezone.utc)
        updated_route = await self.route_repo.update(route, obj_in={})

        return await self.get_route_details(updated_route.id)
