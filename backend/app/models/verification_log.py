from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum, CheckConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import BaseModel
import enum


class VerificationDecision(str, enum.Enum):
    """Verification decisions."""
    VERIFIED = "verified"
    REJECTED = "rejected"
    NEEDS_MORE_INFO = "needs_more_info"


class VerificationLog(BaseModel):
    """Analyst/Authority verification decisions."""
    
    __tablename__ = "verification_logs"
    
    # Foreign Keys
    report_id = Column(String(36), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    verified_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    escalated_to = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Verification Details
    decision = Column(Enum(VerificationDecision), nullable=False)
    comments = Column(Text, nullable=True)
    priority_level = Column(Integer, nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('priority_level >= 1 AND priority_level <= 5', name='check_priority_level'),
    )
    
    # Relationships
    report = relationship("Report", back_populates="verification_logs")
    verifier = relationship("User", back_populates="verification_logs", foreign_keys=[verified_by])
    escalated_to_user = relationship("User", back_populates="escalated_verifications", foreign_keys=[escalated_to])
    
    def __repr__(self):
        return f"<VerificationLog(id={self.id}, decision={self.decision}, report_id={self.report_id})>"
