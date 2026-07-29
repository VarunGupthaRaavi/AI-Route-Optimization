from typing import Dict, List
from pydantic import Field
from app.schemas.base import BaseSchema


class AnalyticsSummary(BaseSchema):
    total_customers: int = Field(default=0, description="Total active customer accounts")
    total_drivers: int = Field(default=0, description="Total registered fleet drivers")
    active_drivers: int = Field(default=0, description="Drivers currently on route or idle")
    total_vehicles: int = Field(default=0, description="Total fleet vehicles")
    available_vehicles: int = Field(default=0, description="Vehicles ready for assignment")
    total_deliveries: int = Field(default=0, description="Total delivery orders")
    pending_deliveries: int = Field(default=0, description="Deliveries awaiting route optimization")
    completed_deliveries: int = Field(default=0, description="Successfully delivered orders")
    in_transit_deliveries: int = Field(default=0, description="Orders currently in transit")
    total_routes: int = Field(default=0, description="Total route plans created")
    active_routes: int = Field(default=0, description="Routes currently in progress")
    completed_routes: int = Field(default=0, description="Fully executed routes")
    delivery_success_rate_pct: float = Field(default=100.0, description="Percentage of successful deliveries")
    fleet_utilization_pct: float = Field(default=0.0, description="Percentage of fleet in active use")
    driver_status_counts: Dict[str, int] = Field(default_factory=dict, description="Driver status breakdown")
    delivery_priority_counts: Dict[str, int] = Field(default_factory=dict, description="Delivery priority breakdown")
