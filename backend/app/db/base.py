"""
Central SQLAlchemy Metadata Registry for Alembic Schema Autogeneration.
Imports all domain models so Base.metadata is fully populated.
"""
from app.models.base import Base  # noqa
from app.models.customer import Customer  # noqa
from app.models.delivery import Delivery  # noqa
from app.models.driver import Driver  # noqa
from app.models.notification import Notification  # noqa
from app.models.route import Route, RouteStop  # noqa
from app.models.user import User  # noqa
from app.models.vehicle import Vehicle  # noqa

__all__ = [
    "Base",
    "User",
    "Customer",
    "Vehicle",
    "Driver",
    "Delivery",
    "Route",
    "RouteStop",
    "Notification",
]
