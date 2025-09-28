from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.db.base_class import BaseModel
from app.db.utils import get_geometry_column, get_jsonb_column, get_inet_column


class AuditLog(BaseModel):
    """Security and analytics audit trail."""
    
    __tablename__ = "audit_logs"
    
    # User Information
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Action Details
    action = Column(String(100), nullable=False, index=True)  # 'login', 'submit_report', 'verify_report', etc.
    resource_type = Column(String(50), nullable=True)  # 'report', 'user', 'hotspot', etc.
    resource_id = Column(String(36), nullable=True)  # ID of the affected resource
    details = Column(get_jsonb_column(), nullable=True)  # Additional context data
    
    # Request Information
    ip_address = Column(get_inet_column(), nullable=True, index=True)  # User's IP address
    user_agent = Column(String(512), nullable=True)  # Browser/app info
    device_fingerprint = Column(String(255), nullable=True)  # For fraud detection
    geolocation = Column(get_geometry_column(srid=4326), nullable=True)  # Request location if available
    session_id = Column(String(36), nullable=True)  # For session tracking
    
    # Result
    success = Column(Boolean, nullable=False, default=True)  # Whether action succeeded
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id})>"
