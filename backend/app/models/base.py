import uuid
from datetime import datetime, timezone
from typing import Any, Dict
from sqlalchemy import Boolean, DateTime, Func, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    SQLAlchemy 2.0 Declarative Base class for all RouteAI database entity models.
    """
    pass


class UUIDMixin:
    """
    Mixin providing a standard UUID primary key column.
    """
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Unique Universal Primary Key Identifier"
    )


class TimestampMixin:
    """
    Mixin providing created_at and updated_at timezone-aware timestamps.
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
        doc="UTC timestamp when entity was created"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="UTC timestamp when entity was last updated"
    )


class SoftDeleteMixin:
    """
    Mixin providing soft deletion capabilities for enterprise data auditing.
    """
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        doc="Soft deletion status indicator"
    )


class BaseModel(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Abstract base model consolidating UUID, Timestamps, and Soft-deletion mixins.
    Serves as the root class for domain entities.
    """
    __abstract__ = True

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts SQLAlchemy model attributes into a serializable Python dictionary.
        """
        result: Dict[str, Any] = {}
        for column in self.__table__.columns:
            val = getattr(self, column.name)
            if isinstance(val, uuid.UUID):
                val = str(val)
            elif isinstance(val, datetime):
                val = val.isoformat()
            result[column.name] = val
        return result

    def __repr__(self) -> str:
        """
        Provides a clean, readable string representation of model instances.
        """
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', 'N/A')})>"
