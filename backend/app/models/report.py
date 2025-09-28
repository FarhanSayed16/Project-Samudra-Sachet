from sqlalchemy import Column, String, Text, Integer, Numeric, ForeignKey, Enum, CheckConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import BaseModel
from app.db.utils import get_geometry_column
import enum


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


class ReportStatus(str, enum.Enum):
    """Report verification status."""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"


class Report(BaseModel):
    """Enhanced citizen reports with geospatial data."""
    
    __tablename__ = "reports"
    
    # Foreign Keys
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Report Content
    hazard_type = Column(Enum(HazardType), nullable=False)
    location = Column(get_geometry_column(srid=4326), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Media
    media_url = Column(String(512), nullable=True)  # S3/Cloudinary URL
    media_thumbnail_url = Column(String(512), nullable=True)  # For quick loading
    
    # Severity and Status
    severity_level = Column(Integer, nullable=False, default=3)
    status = Column(Enum(ReportStatus), nullable=False, default=ReportStatus.PENDING)
    
    # AI and Crowd Scoring
    confidence_score = Column(Numeric(4, 3), nullable=False, default=0.500)  # AI confidence (0.000-1.000)
    crowd_trust_score = Column(Numeric(4, 3), nullable=False, default=0.500)  # Dynamic user credibility
    
    # Engagement Metrics
    view_count = Column(Integer, nullable=False, default=0)
    upvote_count = Column(Integer, nullable=False, default=0)
    downvote_count = Column(Integer, nullable=False, default=0)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('severity_level >= 1 AND severity_level <= 5', name='check_severity_level'),
        CheckConstraint('confidence_score >= 0.000 AND confidence_score <= 1.000', name='check_confidence_score'),
        CheckConstraint('crowd_trust_score >= 0.000 AND crowd_trust_score <= 1.000', name='check_crowd_trust_score'),
    )
    
    # Relationships
    user = relationship("User", back_populates="reports")
    verification_logs = relationship("VerificationLog", back_populates="report", cascade="all, delete-orphan")
    media_analyses = relationship("MediaAnalysis", back_populates="report", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Report(id={self.id}, hazard_type={self.hazard_type}, status={self.status})>"
