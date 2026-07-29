"""
RouteAI Supabase PostgreSQL Database Migration Runner Script.
Applies `supabase/migrations/001_initial_schema.sql` directly to Supabase Cloud PostgreSQL.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.core.logging import logger
import asyncpg


async def run_supabase_migrations():
    """
    Executes the initial SQL migration script against Supabase Managed PostgreSQL.
    """
    logger.info("Initializing Supabase Database Migration Runner...")
    
    # Path to SQL migration file
    root_dir = Path(__file__).resolve().parent.parent.parent
    migration_file = root_dir / "supabase" / "migrations" / "001_initial_schema.sql"

    if not migration_file.exists():
        logger.error(f"Migration file not found at: {migration_file}")
        return False

    with open(migration_file, "r", encoding="utf-8") as f:
        sql_script = f.read()

    # Convert SQLAlchemy connection string (postgresql+asyncpg://...) to standard postgresql:// for asyncpg connection
    db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

    logger.info(f"Connecting to Supabase PostgreSQL target...")
    try:
        conn = await asyncpg.connect(db_url)
        logger.info("Connection established. Applying migration 001_initial_schema.sql...")
        
        await conn.execute(sql_script)
        logger.info("Successfully executed 001_initial_schema.sql migration!")
        
        # Verify created tables
        tables = await conn.fetch(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
        )
        table_names = [r["table_name"] for r in tables]
        logger.info(f"Verified {len(table_names)} public tables in Supabase: {', '.join(table_names)}")

        await conn.close()
        return True

    except Exception as e:
        logger.error(f"Failed to execute Supabase database migration: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_supabase_migrations())
    if not success:
        sys.exit(1)
