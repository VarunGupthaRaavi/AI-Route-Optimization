"""
RouteAI Database Registry Package.
Imports and exposes all SQLAlchemy 2.0 ORM models and Base metadata registry for Supabase schema creation and Alembic migrations.
"""
from app.models.base import Base, BaseModel
from app.models.user import User, UserRole
from app.models.customer import Customer
from app.models.vehicle import Vehicle, VehicleStatus
from app.models.driver import Driver, DriverStatus
from app.models.delivery import Delivery, DeliveryStatus, DeliveryPriority
from app.models.route import Route, RouteStatus, RouteStop
from app.models.notification import Notification, NotificationType
from app.models.knowledge import KnowledgeDocument, KnowledgeChunk

__all__ = [
    "Base",
    "BaseModel",
    "User",
    "UserRole",
    "Customer",
    "Vehicle",
    "VehicleStatus",
    "Driver",
    "DriverStatus",
    "Delivery",
    "DeliveryStatus",
    "DeliveryPriority",
    "Route",
    "RouteStatus",
    "RouteStop",
    "Notification",
    "NotificationType",
    "KnowledgeDocument",
    "KnowledgeChunk",
]
