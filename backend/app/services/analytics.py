from sqlalchemy.ext.asyncio import AsyncSession
from app.models.customer import Customer
from app.models.delivery import Delivery, DeliveryPriority, DeliveryStatus
from app.models.driver import Driver, DriverStatus
from app.models.route import Route, RouteStatus
from app.models.vehicle import Vehicle, VehicleStatus
from app.repositories.customer import CustomerRepository
from app.repositories.delivery import DeliveryRepository
from app.repositories.driver import DriverRepository
from app.repositories.route import RouteRepository
from app.repositories.vehicle import VehicleRepository
from app.schemas.analytics import AnalyticsSummary


class AnalyticsService:
    """
    Business logic service for Executive Logistics Dashboard Analytics & KPI aggregations.
    """
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.customer_repo = CustomerRepository(session)
        self.driver_repo = DriverRepository(session)
        self.vehicle_repo = VehicleRepository(session)
        self.delivery_repo = DeliveryRepository(session)
        self.route_repo = RouteRepository(session)

    async def get_dashboard_summary(self) -> AnalyticsSummary:
        total_cust = await self.customer_repo.count()
        total_driv = await self.driver_repo.count()
        active_driv = await self.driver_repo.count(filters={"status": DriverStatus.ON_ROUTE})
        idle_driv = await self.driver_repo.count(filters={"status": DriverStatus.IDLE})

        total_veh = await self.vehicle_repo.count()
        avail_veh = await self.vehicle_repo.count(filters={"status": VehicleStatus.AVAILABLE})

        total_deliv = await self.delivery_repo.count()
        pending_deliv = await self.delivery_repo.count(filters={"status": DeliveryStatus.PENDING})
        completed_deliv = await self.delivery_repo.count(filters={"status": DeliveryStatus.DELIVERED})
        transit_deliv = await self.delivery_repo.count(filters={"status": DeliveryStatus.IN_TRANSIT})
        failed_deliv = await self.delivery_repo.count(filters={"status": DeliveryStatus.FAILED})

        total_routes = await self.route_repo.count()
        active_routes = await self.route_repo.count(filters={"status": RouteStatus.IN_PROGRESS})
        completed_routes = await self.route_repo.count(filters={"status": RouteStatus.COMPLETED})

        # Calculate Rates
        success_rate = round((completed_deliv / (completed_deliv + failed_deliv) * 100.0), 1) if (completed_deliv + failed_deliv) > 0 else 100.0
        utilization_rate = round((active_driv / total_driv * 100.0), 1) if total_driv > 0 else 0.0

        return AnalyticsSummary(
            total_customers=total_cust,
            total_drivers=total_driv,
            active_drivers=active_driv + idle_driv,
            total_vehicles=total_veh,
            available_vehicles=avail_veh,
            total_deliveries=total_deliv,
            pending_deliveries=pending_deliv,
            completed_deliveries=completed_deliv,
            in_transit_deliveries=transit_deliv,
            total_routes=total_routes,
            active_routes=active_routes,
            completed_routes=completed_routes,
            delivery_success_rate_pct=success_rate,
            fleet_utilization_pct=utilization_rate,
            driver_status_counts={
                "IDLE": idle_driv,
                "ON_ROUTE": active_driv,
                "OFF_DUTY": await self.driver_repo.count(filters={"status": DriverStatus.OFF_DUTY})
            },
            delivery_priority_counts={
                "LOW": await self.delivery_repo.count(filters={"priority": DeliveryPriority.LOW}),
                "MEDIUM": await self.delivery_repo.count(filters={"priority": DeliveryPriority.MEDIUM}),
                "HIGH": await self.delivery_repo.count(filters={"priority": DeliveryPriority.HIGH}),
                "URGENT": await self.delivery_repo.count(filters={"priority": DeliveryPriority.URGENT})
            }
        )
