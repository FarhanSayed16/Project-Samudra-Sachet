from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from app.models.social_media_post import SocialPlatform, Sentiment, HazardType


class SocialMediaPostBase(BaseModel):
    """Base social media post schema with common fields."""
    source_id: str = Field(..., max_length=255)
    source: SocialPlatform
    post_text: Optional[str] = None
    post_url: Optional[str] = Field(None, max_length=512)
    author_username: Optional[str] = Field(None, max_length=100)
    author_verified: bool = False
    post_timestamp: datetime
    language: Optional[str] = Field(None, max_length=10)
    hazard_type: Optional[HazardType] = None
    sentiment: Optional[Sentiment] = None
    sentiment_score: Optional[Decimal] = Field(None, ge=-1.000, le=1.000)
    engagement_count: int = 0
    repost_count: int = 0
    relevance_score: Decimal = Field(default=0.500, ge=0.000, le=1.000)


class SocialMediaPostCreate(SocialMediaPostBase):
    """Schema for creating a new social media post."""
    original_post: Dict[str, Any]
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    location_entities: Optional[Dict[str, Any]] = None


class SocialMediaPostUpdate(BaseModel):
    """Schema for updating social media post."""
    hazard_type: Optional[HazardType] = None
    sentiment: Optional[Sentiment] = None
    sentiment_score: Optional[Decimal] = Field(None, ge=-1.000, le=1.000)
    relevance_score: Optional[Decimal] = Field(None, ge=0.000, le=1.000)


class SocialMediaPostInDB(SocialMediaPostBase):
    """Schema for social media post data in database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    original_post: Dict[str, Any]
    location_entities: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class SocialMediaPost(SocialMediaPostInDB):
    """Schema for social media post data returned by API."""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    @classmethod
    def from_orm_with_location(cls, obj):
        """Create SocialMediaPost instance from ORM object with location extraction."""
        data = obj.__dict__.copy()
        if hasattr(obj, 'location') and obj.location is not None:
            # Extract coordinates from PostGIS geometry
            data['latitude'] = float(obj.location.data['y'])
            data['longitude'] = float(obj.location.data['x'])
        return cls(**data)


class SocialMediaPostSummary(BaseModel):
    """Schema for social media post summary data."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    source: SocialPlatform
    author_username: Optional[str] = None
    post_text: Optional[str] = None
    hazard_type: Optional[HazardType] = None
    sentiment: Optional[Sentiment] = None
    engagement_count: int
    relevance_score: Decimal
    post_timestamp: datetime
