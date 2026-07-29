from datetime import datetime, timezone
from typing import Any, Dict
from fastapi import APIRouter, Request, status
from app import __version__
from app.core.config import settings
from app.core.database import check_database_connection
from app.schemas.base import ResponseModel

router = APIRouter()


@router.get(
    "/health",
    response_model=ResponseModel[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Application Health & Database Connectivity Check",
    description="Performs asynchronous diagnostic verification on backend application services and Supabase PostgreSQL database."
)
async def health_check(request: Request) -> ResponseModel[Dict[str, Any]]:
    """
    Diagnostic Endpoint validating server operational readiness and database pool state.
    """
    db_healthy = await check_database_connection()
    overall_status = "healthy" if db_healthy else "degraded"

    request_id = getattr(request.state, "request_id", None)

    health_payload = {
        "status": overall_status,
        "environment": settings.ENVIRONMENT,
        "version": __version__,
        "database": {
            "connected": db_healthy,
            "engine": "PostgreSQL (asyncpg)"
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    message = "System operational and database connected." if db_healthy else "System running with degraded database connectivity."

    return ResponseModel(
        success=db_healthy,
        data=health_payload,
        message=message,
        request_id=request_id
    )
