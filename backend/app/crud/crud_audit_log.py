from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from geoalchemy2 import functions as geo_func
from app.models.audit_log import AuditLog
from app.models.user import User
import uuid
from datetime import datetime, timedelta


class CRUDAuditLog:
    """CRUD operations for AuditLog model."""
    
    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: Optional[uuid.UUID],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[uuid.UUID] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_fingerprint: Optional[str] = None,
        geolocation: Optional[tuple] = None,  # (lat, lng)
        session_id: Optional[uuid.UUID] = None,
        success: bool = True
    ) -> AuditLog:
        """Create a new audit log entry."""
        # Create PostGIS point from lat/lng if provided
        location_point = None
        if geolocation and len(geolocation) == 2:
            location_point = geo_func.ST_SetSRID(
                geo_func.ST_MakePoint(geolocation[1], geolocation[0]), 
                4326
            )
        
        db_audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            device_fingerprint=device_fingerprint,
            geolocation=location_point,
            session_id=session_id,
            success=success
        )
        
        db.add(db_audit_log)
        await db.commit()
        await db.refresh(db_audit_log)
        return db_audit_log
    
    @staticmethod
    async def get_by_id(db: AsyncSession, log_id: uuid.UUID) -> Optional[AuditLog]:
        """Get audit log by ID."""
        result = await db.execute(
            select(AuditLog)
            .options(selectinload(AuditLog.user))
            .where(AuditLog.id == log_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_audit_logs_with_filters(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        user_id: Optional[uuid.UUID] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        success: Optional[bool] = None,
        ip_address: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[AuditLog], int]:
        """Get audit logs with comprehensive filtering."""
        query = select(AuditLog).options(selectinload(AuditLog.user))
        count_query = select(func.count(AuditLog.id))
        
        # Apply filters
        conditions = []
        
        if user_id:
            conditions.append(AuditLog.user_id == user_id)
        
        if action:
            conditions.append(AuditLog.action == action)
        
        if resource_type:
            conditions.append(AuditLog.resource_type == resource_type)
        
        if success is not None:
            conditions.append(AuditLog.success == success)
        
        if ip_address:
            conditions.append(AuditLog.ip_address == ip_address)
        
        if date_from:
            conditions.append(AuditLog.created_at >= date_from)
        
        if date_to:
            conditions.append(AuditLog.created_at <= date_to)
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Apply sorting
        if sort_by == "created_at":
            sort_column = AuditLog.created_at
        elif sort_by == "action":
            sort_column = AuditLog.action
        else:
            sort_column = AuditLog.created_at
        
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute queries
        result = await db.execute(query)
        logs = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        return logs, total_count
    
    @staticmethod
    async def get_user_activity(
        db: AsyncSession,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
        hours: Optional[int] = None
    ) -> Tuple[List[AuditLog], int]:
        """Get user activity timeline."""
        query = select(AuditLog).where(AuditLog.user_id == user_id)
        count_query = select(func.count(AuditLog.id)).where(AuditLog.user_id == user_id)
        
        # Apply time filter if provided
        if hours:
            since = datetime.utcnow() - timedelta(hours=hours)
            query = query.where(AuditLog.created_at >= since)
            count_query = count_query.where(AuditLog.created_at >= since)
        
        # Sort by creation time (newest first)
        query = query.order_by(AuditLog.created_at.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute queries
        result = await db.execute(query)
        logs = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        return logs, total_count
    
    @staticmethod
    async def get_action_statistics(
        db: AsyncSession,
        hours: int = 24,
        action: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get action statistics."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        query = select(AuditLog).where(AuditLog.created_at >= since)
        
        if action:
            query = query.where(AuditLog.action == action)
        
        result = await db.execute(query)
        logs = result.scalars().all()
        
        # Calculate statistics
        total_actions = len(logs)
        action_counts = {}
        success_count = 0
        failure_count = 0
        unique_users = set()
        unique_ips = set()
        
        for log in logs:
            action_counts[log.action] = action_counts.get(log.action, 0) + 1
            
            if log.success:
                success_count += 1
            else:
                failure_count += 1
            
            if log.user_id:
                unique_users.add(log.user_id)
            
            if log.ip_address:
                unique_ips.add(log.ip_address)
        
        return {
            "total_actions": total_actions,
            "action_counts": action_counts,
            "success_count": success_count,
            "failure_count": failure_count,
            "success_rate": success_count / total_actions if total_actions > 0 else 0,
            "unique_users": len(unique_users),
            "unique_ips": len(unique_ips),
            "time_window_hours": hours
        }
    
    @staticmethod
    async def get_security_events(
        db: AsyncSession,
        hours: int = 24,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[AuditLog], int]:
        """Get security-related events."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Define security-related actions
        security_actions = [
            "login", "logout", "failed_login", "password_change",
            "account_locked", "suspicious_activity", "unauthorized_access"
        ]
        
        query = (
            select(AuditLog)
            .options(selectinload(AuditLog.user))
            .where(
                and_(
                    AuditLog.created_at >= since,
                    AuditLog.action.in_(security_actions)
                )
            )
            .order_by(AuditLog.created_at.desc())
        )
        
        count_query = select(func.count(AuditLog.id)).where(
            and_(
                AuditLog.created_at >= since,
                AuditLog.action.in_(security_actions)
            )
        )
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute queries
        result = await db.execute(query)
        logs = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        return logs, total_count
    
    @staticmethod
    async def get_system_health_metrics(
        db: AsyncSession,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get system health metrics."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Get total activity
        total_query = select(func.count(AuditLog.id)).where(AuditLog.created_at >= since)
        total_result = await db.execute(total_query)
        total_activity = total_result.scalar()
        
        # Get successful vs failed actions
        success_query = select(func.count(AuditLog.id)).where(
            and_(
                AuditLog.created_at >= since,
                AuditLog.success == True
            )
        )
        success_result = await db.execute(success_query)
        successful_actions = success_result.scalar()
        
        failure_query = select(func.count(AuditLog.id)).where(
            and_(
                AuditLog.created_at >= since,
                AuditLog.success == False
            )
        )
        failure_result = await db.execute(failure_query)
        failed_actions = failure_result.scalar()
        
        # Get unique active users
        users_query = select(func.count(func.distinct(AuditLog.user_id))).where(
            and_(
                AuditLog.created_at >= since,
                AuditLog.user_id.isnot(None)
            )
        )
        users_result = await db.execute(users_query)
        active_users = users_result.scalar()
        
        # Calculate health score
        health_score = 100.0
        if total_activity > 0:
            error_rate = failed_actions / total_activity
            health_score = max(0, 100 - (error_rate * 100))
        
        return {
            "total_activity": total_activity,
            "successful_actions": successful_actions,
            "failed_actions": failed_actions,
            "active_users": active_users,
            "health_score": health_score,
            "error_rate": failed_actions / total_activity if total_activity > 0 else 0,
            "time_window_hours": hours
        }
    
    @staticmethod
    async def cleanup_old_logs(db: AsyncSession, days: int = 90) -> int:
        """Clean up old audit logs."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        result = await db.execute(
            select(AuditLog).where(AuditLog.created_at < cutoff_date)
        )
        old_logs = result.scalars().all()
        
        # Delete old logs
        for log in old_logs:
            await db.delete(log)
        
        await db.commit()
        
        return len(old_logs)


# Create instance
crud_audit_log = CRUDAuditLog()
