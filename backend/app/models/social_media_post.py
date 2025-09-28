from sqlalchemy import Column, String, Text, Integer, Numeric, Enum, DateTime, Boolean, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.base_class import BaseModel
from app.db.utils import get_geometry_column, get_jsonb_column
import enum
import os


class SocialPlatform(str, enum.Enum):
    """Social media platforms."""
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TELEGRAM = "telegram"


class Sentiment(str, enum.Enum):
    """Sentiment categories for social media posts."""
    PANIC = "panic"
    CONCERN = "concern"
    NEUTRAL = "neutral"
    AWARENESS = "awareness"
    RELIEF = "relief"


class HazardType(str, enum.Enum):
    """Types of coastal hazards that can be reported."""
    TSUNAMI = "tsunami"
    HIGH_WAVES = "high_waves"
    SWELL_SURGE = "swell_surge"
    COASTAL_FLOODING = "coastal_flooding"
    STORM_SURGE = "storm_surge"
    UNUSUAL_TIDE = "unusual_tide"
    COASTAL_DAMAGE = "coastal_damage"
    COASTAL_CURRENT = "coastal_current"
    OTHER = "other"


class SocialMediaPost(BaseModel):
    """Processed social media data."""
    
    __tablename__ = "social_media_posts"
    
    # Source Information
    source_id = Column(String(255), unique=True, nullable=False, index=True)  # Original platform post ID
    source = Column(Enum(SocialPlatform), nullable=False)
    original_post = Column(get_jsonb_column(), nullable=False)  # Full raw JSON from API
    post_url = Column(String(512), nullable=True)
    
    # Content
    post_text = Column(Text, nullable=True)
    author_username = Column(String(100), nullable=True)
    author_verified = Column(Boolean, nullable=False, default=False)
    post_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    language = Column(String(10), nullable=True)
    
    # Location Data
    location = Column(get_geometry_column(srid=4326), nullable=True, index=True)  # Extracted/inferred location
    location_entities = Column(get_jsonb_column(), nullable=True)  # NER extracted location names
    
    # AI Analysis Results
    hazard_type = Column(Enum(HazardType), nullable=True)
    sentiment = Column(Enum(Sentiment), nullable=True)
    sentiment_score = Column(Numeric(4, 3), nullable=True)  # Detailed sentiment (-1.000 to +1.000)
    
    # Engagement Metrics
    engagement_count = Column(Integer, nullable=False, default=0)  # Likes, shares, retweets
    repost_count = Column(Integer, nullable=False, default=0)
    
    # Relevance Scoring
    relevance_score = Column(Numeric(4, 3), nullable=False, default=0.500)  # How relevant to coastal hazards
    
    # Constraints
    __table_args__ = (
        CheckConstraint('sentiment_score >= -1.000 AND sentiment_score <= 1.000', name='check_sentiment_score'),
        CheckConstraint('relevance_score >= 0.000 AND relevance_score <= 1.000', name='check_relevance_score'),
    )
    
    # Relationships
    media_analyses = relationship("MediaAnalysis", back_populates="social_media_post", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SocialMediaPost(id={self.id}, source={self.source}, source_id={self.source_id})>"
