from fastapi import APIRouter
from app.api.v1.endpoints import (
    ai,
    analytics,
    auth,
    customers,
    deliveries,
    drivers,
    health,
    notifications,
    routes,
    vehicles,
)

api_v1_router = APIRouter()

# Core & System Diagnostics
api_v1_router.include_router(health.router, tags=["System Diagnostics"])
api_v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication & RBAC"])

# AI & Machine Learning Intelligence Suite
api_v1_router.include_router(ai.router, prefix="/ai", tags=["AI Copilot, RAG, Multi-Agent & Predictive ETA"])

# Logistics Business Modules
api_v1_router.include_router(customers.router, prefix="/customers", tags=["Customer Management"])
api_v1_router.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicle Management"])
api_v1_router.include_router(drivers.router, prefix="/drivers", tags=["Driver Management"])
api_v1_router.include_router(deliveries.router, prefix="/deliveries", tags=["Delivery Management & Scheduling"])
api_v1_router.include_router(routes.router, prefix="/routes", tags=["Route Optimization & Driver Allocation"])
api_v1_router.include_router(notifications.router, prefix="/notifications", tags=["Notification Alert Feed"])
api_v1_router.include_router(analytics.router, prefix="/analytics", tags=["Executive Analytics Dashboard"])
