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

# Configure Engine Kwargs (SQLite vs PostgreSQL PgBouncer connection pooling)
engine_kwargs = {
    "echo": settings.DB_ECHO,
}
if not settings.DATABASE_URL.startswith("sqlite"):
    # pyrefly: ignore [no-matching-overload]
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_timeout": settings.DB_POOL_TIMEOUT,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "pool_pre_ping": True,
        "connect_args": {
            "statement_cache_size": 0,
            "prepared_statement_name_func": lambda: ""
        }
    })

# Initialize SQLAlchemy 2.0 Async Engine
engine: AsyncEngine = create_async_engine(
    url=settings.DATABASE_URL,
    **engine_kwargs
)

# Async Session Factory for spawning isolated async database sessions
AsyncSessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Alias for backwards compatibility
AsyncSessionLocal = AsyncSessionFactory


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
