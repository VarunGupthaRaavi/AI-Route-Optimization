import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import DateTime, Enum as SQLEnum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class RouteStatus(str, Enum):
    """
    Optimization route plan lifecycle status.
    """
    DRAFT = "DRAFT"
    OPTIMIZED = "OPTIMIZED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    PLANNED = "PLANNED"


class Route(BaseModel):
    """
    SQLAlchemy 2.0 Route Entity Model.
    Represents an optimized multi-stop logistics route assigned to a vehicle and driver.
    """
    __tablename__ = "routes"

    route_code: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False, doc="Unique route identifier code"
    )
    driver_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("drivers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Assigned driver ID"
    )
    vehicle_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Assigned vehicle ID"
    )
    status: Mapped[RouteStatus] = mapped_column(
        SQLEnum(RouteStatus, name="routestatus", native_enum=False, length=50),
        default=RouteStatus.DRAFT,
        nullable=False,
        index=True,
        doc="Current route lifecycle state"
    )
    total_distance_km: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False, doc="Calculated total route distance in kilometers"
    )
    estimated_duration_minutes: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, doc="Calculated total route duration in minutes"
    )
    total_deliveries: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, doc="Total delivery stops included in this route"
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, doc="Timestamp when route execution started"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, doc="Timestamp when route execution completed"
    )

    def __repr__(self) -> str:
        return f"<Route(id={self.id}, code='{self.route_code}', status='{self.status}')>"


class RouteStop(BaseModel):
    """
    SQLAlchemy 2.0 RouteStop Entity Model.
    Represents an ordered delivery stop on an optimized route.
    """
    __tablename__ = "route_stops"

    route_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("routes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Parent route ID"
    )
    delivery_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("deliveries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Target delivery package ID"
    )
    stop_sequence: Mapped[int] = mapped_column(
        Integer, nullable=False, doc="1-based sequence order of stop on the route"
    )
    estimated_arrival: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, doc="Estimated arrival timestamp at this stop"
    )
    completed: Mapped[bool] = mapped_column(
        default=False, nullable=False, doc="Stop completion status flag"
    )
