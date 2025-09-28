from sqlalchemy import Column, DateTime, func, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func as sql_func
import uuid


# Create the declarative base
Base = declarative_base()


class BaseModel(Base):
    """Base model class with common fields for all tables."""
    
    __abstract__ = True
    
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        comment="Primary key UUID"
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=sql_func.now(),
        nullable=False,
        comment="Timestamp when record was created"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=sql_func.now(),
        onupdate=sql_func.now(),
        nullable=False,
        comment="Timestamp when record was last updated"
    )
    
    def __repr__(self):
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"
