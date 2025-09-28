from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.media_analysis import AnalysisType


class MediaAnalysisBase(BaseModel):
    """Base media analysis schema with common fields."""
    analysis_type: AnalysisType
    model_name: str = Field(..., min_length=1, max_length=100)
    model_version: str = Field(..., min_length=1, max_length=20)
    results: Dict[str, Any] = Field(..., description="Analysis results")
    processing_time_ms: Optional[int] = Field(None, ge=0)


class MediaAnalysisCreate(MediaAnalysisBase):
    """Schema for creating a new media analysis."""
    report_id: Optional[UUID] = None
    post_id: Optional[UUID] = None


class MediaAnalysisUpdate(BaseModel):
    """Schema for updating media analysis."""
    results: Optional[Dict[str, Any]] = None
    processing_time_ms: Optional[int] = Field(None, ge=0)


class MediaAnalysisInDB(MediaAnalysisBase):
    """Schema for media analysis data in database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    report_id: Optional[UUID] = None
    post_id: Optional[UUID] = None
    created_at: datetime


class MediaAnalysis(MediaAnalysisInDB):
    """Schema for media analysis data returned by API."""
    pass



