import uuid
from enum import Enum
from typing import Optional
from sqlalchemy import Enum as SQLEnum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class DriverStatus(str, Enum):
    """
    Duty status indicator for fleet drivers.
    """
    IDLE = "IDLE"
    ON_ROUTE = "ON_ROUTE"
    OFF_DUTY = "OFF_DUTY"


class Driver(BaseModel):
    """
    SQLAlchemy 2.0 Driver Entity Model.
    Represents registered delivery drivers, license qualifications, and vehicle assignments.
    """
    __tablename__ = "drivers"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        doc="Optional link to system User account"
    )
    license_number: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False, doc="Driver commercial license number"
    )
    phone: Mapped[str] = mapped_column(
        String(50), nullable=False, doc="Driver contact phone number"
    )
    status: Mapped[DriverStatus] = mapped_column(
        SQLEnum(DriverStatus, name="driverstatus", native_enum=True),
        default=DriverStatus.IDLE,
        nullable=False,
        index=True,
        doc="Current driver operational status"
    )
    assigned_vehicle_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        nullable=True,
        doc="Currently assigned vehicle ID"
    )
    current_lat: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, doc="Real-time driver location latitude"
    )
    current_lng: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, doc="Real-time driver location longitude"
    )
    rating: Mapped[float] = mapped_column(
        Float, default=5.0, nullable=False, doc="Driver performance rating (1.0 to 5.0)"
    )

    def __repr__(self) -> str:
        return f"<Driver(id={self.id}, license='{self.license_number}', status='{self.status}')>"
