from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import BaseModel
import enum


class UserRole(str, enum.Enum):
    """User roles in the system."""
    CITIZEN = "citizen"
    COASTAL_VOLUNTEER = "coastal_volunteer"
    COASTAL_GUARD = "coastal_guard"
    DISASTER_MANAGER = "disaster_manager"
    ADMIN = "admin"


class User(BaseModel):
    """User model for authentication and user management."""
    
    __tablename__ = "users"
    
    # Basic Information
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(15), nullable=True)
    
    # Role and Permissions
    user_role = Column(Enum(UserRole), nullable=False, default=UserRole.CITIZEN)
    
    # Preferences
    language_preference = Column(String(10), default="en")
    
    # Status Flags
    is_verified = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Profile Information
    profile_picture_url = Column(String(512), nullable=True)
    organization = Column(String(100), nullable=True)  # For volunteers, guards, and managers
    verification_id = Column(String(100), nullable=True)  # For volunteers and guards verification
    is_verified_volunteer = Column(Boolean, nullable=False, default=False)  # For volunteer verification
    
    # Authentication Tracking
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")
    verification_logs = relationship("VerificationLog", back_populates="verifier", foreign_keys="VerificationLog.verified_by")
    escalated_verifications = relationship("VerificationLog", back_populates="escalated_to_user", foreign_keys="VerificationLog.escalated_to")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(email={self.email}, role={self.user_role})>"
