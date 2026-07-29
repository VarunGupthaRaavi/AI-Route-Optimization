import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import Field
from app.models.route import RouteStatus
from app.schemas.base import BaseSchema


class RouteStopResponse(BaseSchema):
    id: uuid.UUID
    route_id: uuid.UUID
    delivery_id: uuid.UUID
    stop_sequence: int
    estimated_arrival: Optional[datetime] = None
    completed: bool


class RouteBase(BaseSchema):
    route_code: Optional[str] = Field(default=None, description="Unique route code identifier")
    driver_id: Optional[uuid.UUID] = Field(default=None, description="Assigned driver ID")
    vehicle_id: Optional[uuid.UUID] = Field(default=None, description="Assigned vehicle ID")
    status: RouteStatus = Field(default=RouteStatus.DRAFT, description="Route status")
    total_distance_km: float = Field(default=0.0, ge=0.0)
    estimated_duration_minutes: int = Field(default=0, ge=0)
    total_deliveries: int = Field(default=0, ge=0)


class RouteCreate(RouteBase):
    delivery_ids: List[uuid.UUID] = Field(default_factory=list, description="List of delivery IDs to optimize")


class RouteUpdate(BaseSchema):
    driver_id: Optional[uuid.UUID] = Field(default=None)
    vehicle_id: Optional[uuid.UUID] = Field(default=None)
    status: Optional[RouteStatus] = Field(default=None)


class DriverAllocationRequest(BaseSchema):
    driver_id: uuid.UUID = Field(..., description="Target driver ID")
    vehicle_id: Optional[uuid.UUID] = Field(default=None, description="Target vehicle ID")


class RouteOptimizeRequest(BaseSchema):
    delivery_ids: List[uuid.UUID] = Field(..., min_length=1, description="List of pending delivery IDs to optimize into a route")
    vehicle_id: Optional[uuid.UUID] = Field(default=None, description="Target vehicle ID for capacity constraints")


class RouteResponse(RouteBase):
    id: uuid.UUID
    route_code: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    stops: List[RouteStopResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
