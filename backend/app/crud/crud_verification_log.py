from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.orm import selectinload
from app.models.verification_log import VerificationLog, VerificationDecision
from app.models.report import Report
from app.models.user import User
from app.schemas.verification_log import VerificationLogCreate, VerificationLogUpdate
import uuid
from datetime import datetime


class CRUDVerificationLog:
    """CRUD operations for VerificationLog model."""
    
    @staticmethod
    async def create(
        db: AsyncSession,
        verification_in: VerificationLogCreate,
        verified_by: uuid.UUID,
        escalated_to: Optional[uuid.UUID] = None
    ) -> VerificationLog:
        """Create a new verification log."""
        db_verification = VerificationLog(
            report_id=verification_in.report_id,
            verified_by=verified_by,
            escalated_to=escalated_to,
            decision=verification_in.decision,
            comments=verification_in.comments,
            priority_level=verification_in.priority_level
        )
        
        db.add(db_verification)
        await db.commit()
        await db.refresh(db_verification)
        return db_verification
    
    @staticmethod
    async def get_by_id(db: AsyncSession, verification_id: uuid.UUID) -> Optional[VerificationLog]:
        """Get verification log by ID."""
        result = await db.execute(
            select(VerificationLog)
            .options(selectinload(VerificationLog.report))
            .options(selectinload(VerificationLog.verifier))
            .options(selectinload(VerificationLog.escalated_to_user))
            .where(VerificationLog.id == verification_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_report_id(
        db: AsyncSession, 
        report_id: uuid.UUID
    ) -> List[VerificationLog]:
        """Get all verification logs for a report."""
        result = await db.execute(
            select(VerificationLog)
            .options(selectinload(VerificationLog.verifier))
            .options(selectinload(VerificationLog.escalated_to_user))
            .where(VerificationLog.report_id == report_id)
            .order_by(VerificationLog.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_by_verifier(
        db: AsyncSession,
        verifier_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[VerificationLog], int]:
        """Get verification logs by verifier."""
        query = (
            select(VerificationLog)
            .options(selectinload(VerificationLog.report))
            .where(VerificationLog.verified_by == verifier_id)
            .order_by(VerificationLog.created_at.desc())
        )
        
        count_query = select(func.count(VerificationLog.id)).where(
            VerificationLog.verified_by == verifier_id
        )
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute queries
        result = await db.execute(query)
        verifications = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        return verifications, total_count
    
    @staticmethod
    async def get_pending_verifications(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Report], int]:
        """Get reports pending verification."""
        query = (
            select(Report)
            .options(selectinload(Report.user))
            .where(Report.status == "pending")
            .order_by(Report.created_at.desc())
        )
        
        count_query = select(func.count(Report.id)).where(Report.status == "pending")
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute queries
        result = await db.execute(query)
        reports = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        return reports, total_count
    
    @staticmethod
    async def update(
        db: AsyncSession,
        db_verification: VerificationLog,
        verification_in: VerificationLogUpdate
    ) -> VerificationLog:
        """Update verification log."""
        update_data = verification_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_verification, field, value)
        
        await db.commit()
        await db.refresh(db_verification)
        return db_verification
    
    @staticmethod
    async def escalate_verification(
        db: AsyncSession,
        verification_id: uuid.UUID,
        escalated_to: uuid.UUID,
        comments: Optional[str] = None
    ) -> Optional[VerificationLog]:
        """Escalate verification to higher authority."""
        result = await db.execute(
            update(VerificationLog)
            .where(VerificationLog.id == verification_id)
            .values(
                escalated_to=escalated_to,
                comments=comments or "Escalated to higher authority"
            )
            .returning(VerificationLog)
        )
        
        updated_verification = result.scalar_one_or_none()
        if updated_verification:
            await db.commit()
            await db.refresh(updated_verification)
        
        return updated_verification
    
    @staticmethod
    async def get_verification_stats(
        db: AsyncSession,
        verifier_id: Optional[uuid.UUID] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> dict:
        """Get verification statistics."""
        query = select(VerificationLog)
        
        conditions = []
        if verifier_id:
            conditions.append(VerificationLog.verified_by == verifier_id)
        if date_from:
            conditions.append(VerificationLog.created_at >= date_from)
        if date_to:
            conditions.append(VerificationLog.created_at <= date_to)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        result = await db.execute(query)
        verifications = result.scalars().all()
        
        # Calculate statistics
        total_verifications = len(verifications)
        verified_count = sum(1 for v in verifications if v.decision == VerificationDecision.VERIFIED)
        rejected_count = sum(1 for v in verifications if v.decision == VerificationDecision.REJECTED)
        needs_info_count = sum(1 for v in verifications if v.decision == VerificationDecision.NEEDS_MORE_INFO)
        
        return {
            "total_verifications": total_verifications,
            "verified_count": verified_count,
            "rejected_count": rejected_count,
            "needs_info_count": needs_info_count,
            "verification_rate": verified_count / total_verifications if total_verifications > 0 else 0
        }
    
    @staticmethod
    async def delete(db: AsyncSession, verification_id: uuid.UUID) -> bool:
        """Delete verification log."""
        result = await db.execute(
            select(VerificationLog).where(VerificationLog.id == verification_id)
        )
        verification = result.scalar_one_or_none()
        
        if not verification:
            return False
        
        await db.delete(verification)
        await db.commit()
        return True


# Create instance
crud_verification_log = CRUDVerificationLog()
