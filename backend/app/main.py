from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app import __version__
from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.database import check_database_connection, engine
from app.core.exceptions import register_exception_handlers
from app.core.logging import logger
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.timing import TimingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI Lifespan Context Manager handling application startup and shutdown lifecycle events.
    Verifies database connectivity on boot and cleans up resource pools on shutdown.
    """
    logger.info(f"Starting {settings.PROJECT_NAME} v{__version__} [{settings.ENVIRONMENT}]")
    db_ok = await check_database_connection()
    if db_ok:
        logger.info("Database connection successfully established and validated.")
    else:
        logger.warning("Database connection health check failed during startup sequence.")

    yield

    logger.info("Shutting down application server and disposing database connection pool...")
    await engine.dispose()
    logger.info("Database engine pool disposed cleanly. Shutdown complete.")


def create_application() -> FastAPI:
    """
    Application Factory constructing and configuring the FastAPI server instance.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=__version__,
        description="Enterprise AI-Powered Logistics Route Optimization Platform API",
        openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )

    # Configure CORS Middleware for cross-origin frontend requests
    if settings.CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["X-Request-ID", "X-Process-Time"]
        )

    # Register Custom ASGI Middlewares
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # Register Centralized Exception Handlers
    register_exception_handlers(app)

    # Mount API Router (v1)
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)

    @app.get("/", status_code=status.HTTP_200_OK, include_in_schema=False)
    async def root_redirect() -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "name": settings.PROJECT_NAME,
                "version": __version__,
                "environment": settings.ENVIRONMENT,
                "status": "online",
                "docs": "/docs" if settings.DEBUG else "disabled"
            }
        )

    return app


app = create_application()
