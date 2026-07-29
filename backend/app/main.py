from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select
from app import __version__
from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.database import check_database_connection, engine, AsyncSessionLocal
from app.core.exceptions import register_exception_handlers
from app.core.logging import logger
from app.core.security import get_password_hash, verify_password
from app.db.base import Base
from app.models.user import User, UserRole
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.timing import TimingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI Lifespan Context Manager handling application startup and shutdown lifecycle events.
    Verifies database connectivity on boot, auto-creates tables, seeds default admin, and disposes pools on shutdown.
    """
    logger.info(f"Starting {settings.PROJECT_NAME} v{__version__} [{settings.ENVIRONMENT}]")
    
    # Auto-create missing database tables & seed admin user on startup
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema tables auto-verified and created.")

        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.email == "admin@routeai.com"))
            admin_user = result.scalar_one_or_none()
            if not admin_user:
                admin_user = User(
                    email="admin@routeai.com",
                    password_hash=get_password_hash("admin123"),
                    full_name="System Administrator",
                    role=UserRole.ADMIN.value,
                    is_active=True
                )
                session.add(admin_user)
                await session.commit()
                logger.info("Default admin user auto-seeded (admin@routeai.com / admin123).")
            elif not verify_password("admin123", admin_user.password_hash):
                # Auto-heal invalid seed password hash
                admin_user.password_hash = get_password_hash("admin123")
                await session.commit()
                logger.info("Auto-healed admin user password hash for admin@routeai.com.")
    except Exception as e:
        logger.warning(f"Database schema auto-creation notice: {e}")

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

    # Enable Permissive CORS Middleware for local dev & production clients
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
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
