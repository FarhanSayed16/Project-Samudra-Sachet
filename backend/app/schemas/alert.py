from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class AlertBase(BaseModel):
    """Base alert schema with common fields."""
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    alert_level: int = Field(..., ge=1, le=5)
    alert_type: str = Field(..., pattern="^(emergency|warning|info)$")
    target_audience: str = Field(..., pattern="^(all_citizens|coastal_citizens|authorities|analysts)$")
    geographic_scope: Optional[str] = Field(None, max_length=200)


class AlertCreate(AlertBase):
    """Schema for creating a new alert."""
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    delivery_channels: Optional[List[str]] = Field(default=["push_notification"])
    metadata: Optional[Dict[str, Any]] = None


class AlertUpdate(BaseModel):
    """Schema for updating alert."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    message: Optional[str] = Field(None, min_length=1, max_length=1000)
    alert_level: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[str] = Field(None, pattern="^(pending|sent|delivered|failed|cancelled)$")


class AlertInDB(AlertBase):
    """Schema for alert data in database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_by: UUID
    created_at: datetime
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    status: str
    recipients_count: int = 0
    delivery_status: str = "pending"
    delivery_channels: List[str] = []
    metadata: Optional[Dict[str, Any]] = None


class Alert(AlertInDB):
    """Schema for alert data returned by API."""
    pass


class AlertTemplate(BaseModel):
    """Schema for alert template."""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=100)
    title_template: str = Field(..., min_length=1, max_length=200)
    message_template: str = Field(..., min_length=1, max_length=1000)
    alert_level: int = Field(..., ge=1, le=5)
    alert_type: str = Field(..., pattern="^(emergency|warning|info)$")
    target_audience: str = Field(..., pattern="^(all_citizens|coastal_citizens|authorities|analysts)$")
    variables: Optional[List[str]] = None
    created_by: Optional[UUID] = None
    created_at: Optional[datetime] = None


class AlertStats(BaseModel):
    """Schema for alert statistics."""
    time_window_hours: int
    total_alerts: int
    alerts_by_level: Dict[str, int]
    alerts_by_type: Dict[str, int]
    delivery_stats: Dict[str, Any]
    average_response_time_minutes: float
    generated_at: datetime
