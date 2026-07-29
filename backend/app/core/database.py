from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.core.config import settings
from app.core.logging import logger

# Initialize SQLAlchemy 2.0 Async Engine with production-grade connection pooling
engine: AsyncEngine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,  # Proactively test connection validity before checked out from pool
)

# Async Session Factory for spawning isolated async database sessions
AsyncSessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevents unnecessary attribute refreshes after commit in SQLAlchemy 2.0
    autoflush=False,
    autocommit=False,
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI Dependency yielding an AsyncSession instance per request.
    Ensures safe resource cleanup and transaction rollback on unhandled exceptions.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.error(f"Database transaction rolled back due to error: {str(exc)}", exc_info=True)
            raise
        finally:
            await session.close()


async def check_database_connection() -> bool:
    """
    Executes a lightweight query ('SELECT 1') against the database engine
    to verify active pool and server connectivity. Returns True if healthy.
    """
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            val = result.scalar()
            return val == 1
    except Exception as exc:
        logger.error(f"Database health check failed: {str(exc)}")
        return False
