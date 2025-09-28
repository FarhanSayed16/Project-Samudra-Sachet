from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.hotspot import HazardType, HotspotStatus


class HotspotBase(BaseModel):
    """Base hotspot schema with common fields."""
    event_type: HazardType
    radius_km: float = Field(..., gt=0)
    intensity_score: float = Field(..., ge=0.000, le=1.000)
    alert_level: int = Field(default=1, ge=1, le=5)
    status: HotspotStatus = HotspotStatus.ACTIVE
    first_reported_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    hotspot_metadata: Optional[Dict[str, Any]] = None


class HotspotCreate(HotspotBase):
    """Schema for creating a new hotspot."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class HotspotUpdate(BaseModel):
    """Schema for updating hotspot."""
    intensity_score: Optional[float] = Field(None, ge=0.000, le=1.000)
    alert_level: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[HotspotStatus] = None
    report_count: Optional[int] = None
    social_count: Optional[int] = None
    verified_report_count: Optional[int] = None
    last_activity_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    hotspot_metadata: Optional[Dict[str, Any]] = None


class HotspotInDB(HotspotBase):
    """Schema for hotspot data in database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    report_count: int = 0
    social_count: int = 0
    verified_report_count: int = 0
    created_at: datetime
    updated_at: datetime


class Hotspot(HotspotInDB):
    """Schema for hotspot data returned by API."""
    latitude: float
    longitude: float
    
    @classmethod
    def from_orm_with_location(cls, obj):
        """Create Hotspot instance from ORM object with location extraction."""
        data = obj.__dict__.copy()
        if hasattr(obj, 'location') and obj.location is not None:
            # Extract coordinates from PostGIS geometry
            data['latitude'] = float(obj.location.data['y'])
            data['longitude'] = float(obj.location.data['x'])
        return cls(**data)


class HotspotSummary(BaseModel):
    """Schema for hotspot summary data."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    event_type: HazardType
    status: HotspotStatus
    intensity_score: float
    alert_level: int
    report_count: int
    verified_report_count: int
    created_at: datetime
    latitude: float
    longitude: float
