"""
Database utilities for handling different database types.
"""

from sqlalchemy import Text, String
from app.core.config import settings

def get_geometry_column(srid=4326, **kwargs):
    """
    Get appropriate geometry column type based on database.
    For PostgreSQL: Uses geoalchemy2 Geometry
    For SQLite: Uses Text to store WKT (Well-Known Text)
    """
    if "postgresql" in settings.DATABASE_URL:
        from geoalchemy2 import Geometry
        return Geometry("Point", srid=srid, **kwargs)
    else:
        # For SQLite, use Text to store geometry as WKT
        return Text(**kwargs)

def get_uuid_column(**kwargs):
    """
    Get appropriate UUID column type based on database.
    For PostgreSQL: Uses UUID
    For SQLite: Uses String(36)
    """
    if "postgresql" in settings.DATABASE_URL:
        from sqlalchemy.dialects.postgresql import UUID
        return UUID(as_uuid=True, **kwargs)
    else:
        return String(36, **kwargs)

def get_jsonb_column(**kwargs):
    """
    Get appropriate JSON column type based on database.
    For PostgreSQL: Uses JSONB
    For SQLite: Uses Text
    """
    if "postgresql" in settings.DATABASE_URL:
        from sqlalchemy.dialects.postgresql import JSONB
        return JSONB(**kwargs)
    else:
        return Text(**kwargs)

def get_inet_column(**kwargs):
    """
    Get appropriate IP address column type based on database.
    For PostgreSQL: Uses INET
    For SQLite: Uses String(45)
    """
    if "postgresql" in settings.DATABASE_URL:
        from sqlalchemy.dialects.postgresql import INET
        return INET(**kwargs)
    else:
        return String(45, **kwargs)