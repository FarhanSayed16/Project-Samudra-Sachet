from sqlalchemy import Column, String, Integer, ForeignKey, Enum, CheckConstraint, Text
from sqlalchemy.orm import relationship
from app.db.base_class import BaseModel
from app.db.utils import get_jsonb_column
import enum


class AnalysisType(str, enum.Enum):
    """Types of AI analysis performed."""
    IMAGE_CLASSIFICATION = "image_classification"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    NER_EXTRACTION = "ner_extraction"
    HAZARD_DETECTION = "hazard_detection"


class MediaAnalysis(BaseModel):
    """AI analysis results for reports and social media posts."""
    
    __tablename__ = "media_analysis"
    
    # Foreign Keys (at least one must be present)
    report_id = Column(String(36), ForeignKey("reports.id", ondelete="CASCADE"), nullable=True)
    post_id = Column(String(36), ForeignKey("social_media_posts.id", ondelete="CASCADE"), nullable=True)
    
    # Analysis Details
    analysis_type = Column(Enum(AnalysisType), nullable=False)
    model_name = Column(String(100), nullable=True)  # Which AI model was used
    model_version = Column(String(20), nullable=True)
    results = Column(get_jsonb_column(), nullable=False)  # Detailed analysis results
    
    # Performance Tracking
    processing_time_ms = Column(Integer, nullable=True)  # Performance tracking
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            '(report_id IS NOT NULL) OR (post_id IS NOT NULL)',
            name='media_analysis_source_check'
        ),
    )
    
    # Relationships
    report = relationship("Report", back_populates="media_analyses")
    social_media_post = relationship("SocialMediaPost", back_populates="media_analyses")
    
    def __repr__(self):
        return f"<MediaAnalysis(id={self.id}, type={self.analysis_type}, model={self.model_name})>"
