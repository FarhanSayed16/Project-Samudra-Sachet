# Import all models to ensure they are registered with SQLAlchemy
from .user import User, UserRole
from .report import Report, HazardType, ReportStatus
from .verification_log import VerificationLog, VerificationDecision
from .social_media_post import SocialMediaPost, SocialPlatform, Sentiment
from .media_analysis import MediaAnalysis, AnalysisType
from .hotspot import Hotspot, HotspotStatus
from .audit_log import AuditLog

__all__ = [
    "User",
    "UserRole",
    "Report", 
    "HazardType",
    "ReportStatus",
    "VerificationLog",
    "VerificationDecision",
    "SocialMediaPost",
    "SocialPlatform",
    "Sentiment",
    "MediaAnalysis",
    "AnalysisType",
    "Hotspot",
    "HotspotStatus",
    "AuditLog",
]
