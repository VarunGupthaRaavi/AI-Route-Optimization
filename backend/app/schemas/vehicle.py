import uuid
from datetime import datetime
from typing import Optional
from pydantic import Field
from app.models.vehicle import VehicleStatus
from app.schemas.base import BaseSchema


class VehicleBase(BaseSchema):
    license_plate: str = Field(..., min_length=2, max_length=50, description="License plate number")
    vehicle_model: str = Field(..., min_length=2, max_length=100, description="Vehicle make and model")
    capacity_kg: float = Field(..., gt=0.0, description="Payload weight capacity in kg")
    volume_m3: float = Field(..., gt=0.0, description="Cargo volume capacity in m3")
    fuel_type: str = Field(default="DIESEL", description="Fuel / energy type")
    max_range_km: float = Field(default=500.0, gt=0.0, description="Maximum driving range in km")
    status: VehicleStatus = Field(default=VehicleStatus.AVAILABLE, description="Vehicle status")
    current_lat: Optional[float] = Field(default=None, ge=-90.0, le=90.0)
    current_lng: Optional[float] = Field(default=None, ge=-180.0, le=180.0)


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseSchema):
    license_plate: Optional[str] = Field(default=None, min_length=2, max_length=50)
    vehicle_model: Optional[str] = Field(default=None, min_length=2, max_length=100)
    capacity_kg: Optional[float] = Field(default=None, gt=0.0)
    volume_m3: Optional[float] = Field(default=None, gt=0.0)
    fuel_type: Optional[str] = Field(default=None)
    max_range_km: Optional[float] = Field(default=None, gt=0.0)
    status: Optional[VehicleStatus] = Field(default=None)
    current_lat: Optional[float] = Field(default=None, ge=-90.0, le=90.0)
    current_lng: Optional[float] = Field(default=None, ge=-180.0, le=180.0)


class VehicleResponse(VehicleBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
