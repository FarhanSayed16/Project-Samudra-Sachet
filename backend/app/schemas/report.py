from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from app.models.report import HazardType, ReportStatus


class ReportBase(BaseModel):
    """Base report schema with common fields."""
    hazard_type: HazardType
    description: Optional[str] = None
    severity_level: int = Field(default=3, ge=1, le=5)
    media_url: Optional[str] = Field(None, max_length=512)
    media_thumbnail_url: Optional[str] = Field(None, max_length=512)


class ReportCreate(ReportBase):
    """Schema for creating a new report."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class ReportUpdate(BaseModel):
    """Schema for updating report information."""
    description: Optional[str] = None
    severity_level: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[ReportStatus] = None


class ReportInDB(ReportBase):
    """Schema for report data in database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    status: ReportStatus
    confidence_score: Decimal
    crowd_trust_score: Decimal
    view_count: int
    upvote_count: int
    downvote_count: int
    created_at: datetime
    updated_at: datetime


class Report(ReportInDB):
    """Schema for report data returned by API."""
    latitude: float
    longitude: float
    
    @classmethod
    def from_orm_with_location(cls, obj):
        """Create Report instance from ORM object with location extraction."""
        data = obj.__dict__.copy()
        if hasattr(obj, 'location') and obj.location is not None:
            # Extract coordinates from PostGIS geometry
            data['latitude'] = float(obj.location.data['y'])
            data['longitude'] = float(obj.location.data['x'])
        return cls(**data)


class ReportResponse(BaseModel):
    """Schema for report response (public data only)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    hazard_type: HazardType
    status: ReportStatus
    severity_level: int
    description: Optional[str] = None
    media_url: Optional[str] = None
    media_thumbnail_url: Optional[str] = None
    confidence_score: Decimal
    crowd_trust_score: Decimal
    view_count: int
    upvote_count: int
    downvote_count: int
    created_at: datetime
    latitude: float
    longitude: float


class ReportWithUser(Report):
    """Schema for report data with user information."""
    user: Optional[dict] = None  # Will contain user info


class ReportSummary(BaseModel):
    """Schema for report summary data."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    hazard_type: HazardType
    status: ReportStatus
    severity_level: int
    confidence_score: Decimal
    created_at: datetime
    latitude: float
    longitude: float
