from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Set to True for SQL query logging
    future=True,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False,
)


async def get_db() -> AsyncSession:
    """
    Dependency to get database session.
    Use this in FastAPI endpoints with Depends(get_db).
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    from app.db.base_class import Base
    import os
    
    async with engine.begin() as conn:
        # Import all models to ensure they are registered
        from app.models import (
            user,
            report,
            verification_log,
            social_media_post,
            media_analysis,
            hotspot,
            audit_log,
        )
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        
        # Only initialize PostGIS for PostgreSQL
        if "postgresql" in settings.DATABASE_URL:
            # Initialize PostGIS extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
            await conn.execute("CREATE EXTENSION IF NOT EXISTS postgis_topology;")
            await conn.execute("CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;")
            await conn.execute("CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;")


async def close_db():
    """Close database connections."""
    await engine.dispose()
