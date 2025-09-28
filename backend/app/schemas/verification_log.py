from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.verification_log import VerificationDecision


class VerificationLogBase(BaseModel):
    """Base verification log schema with common fields."""
    decision: VerificationDecision
    comments: Optional[str] = None
    priority_level: Optional[int] = Field(None, ge=1, le=5)


class VerificationLogCreate(VerificationLogBase):
    """Schema for creating a new verification log."""
    report_id: UUID


class VerificationLogUpdate(BaseModel):
    """Schema for updating verification log."""
    decision: Optional[VerificationDecision] = None
    comments: Optional[str] = None
    priority_level: Optional[int] = Field(None, ge=1, le=5)
    escalated_to: Optional[UUID] = None


class VerificationLogInDB(VerificationLogBase):
    """Schema for verification log data in database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    report_id: UUID
    verified_by: UUID
    escalated_to: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class VerificationLog(VerificationLogInDB):
    """Schema for verification log data returned by API."""
    pass


class VerificationLogWithDetails(VerificationLog):
    """Schema for verification log with additional details."""
    verifier_name: Optional[str] = None
    escalated_to_name: Optional[str] = None
