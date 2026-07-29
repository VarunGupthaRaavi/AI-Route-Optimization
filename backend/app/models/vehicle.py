from enum import Enum
from typing import Optional
from sqlalchemy import Enum as SQLEnum, Float, String
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class VehicleStatus(str, Enum):
    """
    Operational status indicator for fleet vehicles.
    """
    AVAILABLE = "AVAILABLE"
    IN_TRANSIT = "IN_TRANSIT"
    MAINTENANCE = "MAINTENANCE"


class Vehicle(BaseModel):
    """
    SQLAlchemy 2.0 Vehicle Entity Model.
    Represents logistics fleet vehicles, capacities, and real-time telemetry coordinates.
    """
    __tablename__ = "vehicles"

    license_plate: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False, doc="Unique license plate number"
    )
    vehicle_model: Mapped[str] = mapped_column(
        String(100), nullable=False, doc="Vehicle make and model description"
    )
    capacity_kg: Mapped[float] = mapped_column(
        Float, nullable=False, doc="Maximum payload weight capacity in kilograms"
    )
    volume_m3: Mapped[float] = mapped_column(
        Float, nullable=False, doc="Maximum cargo volume capacity in cubic meters"
    )
    fuel_type: Mapped[str] = mapped_column(
        String(50), default="DIESEL", nullable=False, doc="Fuel or power source type (DIESEL, ELECTRIC, GASOLINE)"
    )
    max_range_km: Mapped[float] = mapped_column(
        Float, default=500.0, nullable=False, doc="Maximum driving range in kilometers per full tank/charge"
    )
    status: Mapped[VehicleStatus] = mapped_column(
        SQLEnum(VehicleStatus, name="vehiclestatus", native_enum=True),
        default=VehicleStatus.AVAILABLE,
        nullable=False,
        index=True,
        doc="Operational fleet status"
    )
    current_lat: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, doc="Last reported telemetry latitude"
    )
    current_lng: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, doc="Last reported telemetry longitude"
    )

    def __repr__(self) -> str:
        return f"<Vehicle(id={self.id}, plate='{self.license_plate}', status='{self.status}')>"
