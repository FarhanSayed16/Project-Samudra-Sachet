from sqlalchemy import Column, String, Integer, Numeric, Enum, DateTime, CheckConstraint, Text
from sqlalchemy.orm import relationship
from app.db.base_class import BaseModel
from app.db.utils import get_geometry_column, get_jsonb_column
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


class HotspotStatus(str, enum.Enum):
    """Hotspot status."""
    ACTIVE = "active"
    MONITORING = "monitoring"
    RESOLVED = "resolved"


class Hotspot(BaseModel):
    """Dynamic event clusters for hazard monitoring."""
    
    __tablename__ = "hotspots"
    
    # Event Information
    event_type = Column(Enum(HazardType), nullable=False)
    location = Column(get_geometry_column(srid=4326), nullable=False, index=True)  # Center point
    radius_km = Column(Numeric(6, 2), nullable=False)  # Affected radius
    
    # Intensity and Scoring
    intensity_score = Column(Numeric(4, 3), nullable=False)  # 0.000-1.000 based on density + severity
    alert_level = Column(Integer, nullable=False, default=1)
    
    # Counts
    report_count = Column(Integer, nullable=False, default=0)
    social_count = Column(Integer, nullable=False, default=0)
    verified_report_count = Column(Integer, nullable=False, default=0)
    
    # Status and Timing
    status = Column(Enum(HotspotStatus), nullable=False, default=HotspotStatus.ACTIVE)
    first_reported_at = Column(DateTime(timezone=True), nullable=True)
    last_activity_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Auto-cleanup old hotspots
    
    # Additional Context
    hotspot_metadata = Column(get_jsonb_column(), nullable=True)  # Additional context (weather data, etc.)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('alert_level >= 1 AND alert_level <= 5', name='check_alert_level'),
        CheckConstraint('intensity_score >= 0.000 AND intensity_score <= 1.000', name='check_intensity_score'),
        CheckConstraint('radius_km > 0', name='check_radius_positive'),
    )
    
    def __repr__(self):
        return f"<Hotspot(id={self.id}, event_type={self.event_type}, status={self.status})>"
