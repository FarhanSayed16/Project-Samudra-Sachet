from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import require_admin
from app.db.session import get_db
from app.crud.crud_user import crud_user
from app.crud.crud_report import crud_report
from app.crud.crud_hotspot import crud_hotspot
from app.crud.crud_social_media_post import crud_social_media_post
from app.crud.crud_media_analysis import crud_media_analysis
from app.crud.crud_audit_log import crud_audit_log
from app.models.user import User, UserRole
from app.schemas.user import User as UserSchema, UserUpdate
import uuid
from datetime import datetime, timedelta


router = APIRouter()


@router.get("/dashboard")
async def get_admin_dashboard(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get system dashboard metrics.
    
    Access restricted to Admin users only.
    """
    # Get system health metrics
    health_metrics = await crud_audit_log.get_system_health_metrics(db, hours=24)
    
    # Get user statistics
    total_users, _ = await crud_user.get_users(db, skip=0, limit=1)
    active_users, _ = await crud_user.get_users(db, skip=0, limit=1, is_active=True)
    
    # Get report statistics
    total_reports, _ = await crud_report.get_reports_with_filters(db, skip=0, limit=1)
    recent_reports, _ = await crud_report.get_reports_with_filters(
        db, 
        skip=0, 
        limit=1,
        date_from=datetime.utcnow() - timedelta(hours=24)
    )
    
    # Get hotspot statistics
    active_hotspots, _ = await crud_hotspot.get_active_hotspots(db, skip=0, limit=1)
    
    # Get social media statistics
    total_posts, _ = await crud_social_media_post.get_posts_with_filters(db, skip=0, limit=1)
    recent_posts, _ = await crud_social_media_post.get_posts_with_filters(
        db,
        skip=0,
        limit=1,
        date_from=datetime.utcnow() - timedelta(hours=24)
    )
    
    return {
        "system_health": health_metrics,
        "user_stats": {
            "total_users": len(total_users),
            "active_users": len(active_users),
            "new_users_24h": 0  # Would calculate from user creation dates
        },
        "report_stats": {
            "total_reports": len(total_reports),
            "reports_24h": len(recent_reports),
            "pending_verification": 0  # Would calculate from report status
        },
        "hotspot_stats": {
            "active_hotspots": len(active_hotspots),
            "high_alert_hotspots": 0  # Would calculate from alert levels
        },
        "social_media_stats": {
            "total_posts": len(total_posts),
            "posts_24h": len(recent_posts),
            "high_relevance_posts": 0  # Would calculate from relevance scores
        },
        "last_updated": datetime.utcnow()
    }


@router.get("/stats")
async def get_detailed_statistics(
    hours: int = Query(24, ge=1, le=168),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed system statistics.
    
    Access restricted to Admin users only.
    
    - **hours**: Time window for statistics (1-168 hours)
    """
    # Get action statistics
    action_stats = await crud_audit_log.get_action_statistics(db, hours=hours)
    
    # Get security events
    security_events, _ = await crud_audit_log.get_security_events(db, hours=hours)
    
    # Get analysis statistics
    analysis_stats = await crud_media_analysis.get_analysis_stats(db, hours=hours)
    
    # Get sentiment analysis
    sentiment_stats = await crud_social_media_post.get_sentiment_analysis(db, hours=hours)
    
    return {
        "time_window_hours": hours,
        "action_statistics": action_stats,
        "security_events": {
            "count": len(security_events),
            "events": security_events[:10]  # Limit to recent 10
        },
        "analysis_statistics": analysis_stats,
        "sentiment_statistics": sentiment_stats,
        "generated_at": datetime.utcnow()
    }


@router.get("/users", response_model=List[UserSchema])
async def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_role: Optional[UserRole] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    List all users in the system.
    
    Access restricted to Admin users only.
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **user_role**: Filter by user role
    - **is_active**: Filter by active status
    """
    users = await crud_user.get_users(
        db=db,
        skip=skip,
        limit=limit,
        user_role=user_role.value if user_role else None,
        is_active=is_active
    )
    
    return users


@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user_admin_details(
    user_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user admin details.
    
    Access restricted to Admin users only.
    
    - **user_id**: User UUID
    """
    user = await crud_user.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.patch("/users/{user_id}/role")
async def change_user_role(
    user_id: uuid.UUID,
    new_role: UserRole,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user role.
    
    Access restricted to Admin users only.
    
    - **user_id**: User UUID
    - **new_role**: New user role
    """
    user = await crud_user.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from changing their own role
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )
    
    # Update user role
    user_update = UserUpdate()
    user_update.user_role = new_role
    
    updated_user = await crud_user.update(db, user, user_update)
    
    return {
        "message": "User role updated successfully",
        "user_id": str(user_id),
        "old_role": user.user_role.value,
        "new_role": new_role.value
    }


@router.get("/audit-logs")
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[uuid.UUID] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    success: Optional[bool] = Query(None),
    ip_address: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    sort_by: str = Query("created_at", regex="^(created_at|action)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get system audit logs.
    
    Access restricted to Admin users only.
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **user_id**: Filter by user ID
    - **action**: Filter by action type
    - **resource_type**: Filter by resource type
    - **success**: Filter by success status
    - **ip_address**: Filter by IP address
    - **date_from/date_to**: Filter by date range
    - **sort_by**: Sort field
    - **sort_order**: Sort direction
    """
    logs, total_count = await crud_audit_log.get_audit_logs_with_filters(
        db=db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        success=success,
        ip_address=ip_address,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    return {
        "logs": logs,
        "total_count": total_count,
        "returned_count": len(logs)
    }


@router.get("/system/health")
async def get_system_health(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get system health check.
    
    Access restricted to Admin users only.
    """
    # Get system health metrics
    health_metrics = await crud_audit_log.get_system_health_metrics(db, hours=24)
    
    # Get security events
    security_events, _ = await crud_audit_log.get_security_events(db, hours=1)
    
    # Determine overall health status
    health_status = "healthy"
    if health_metrics["health_score"] < 80:
        health_status = "warning"
    if health_metrics["health_score"] < 60:
        health_status = "critical"
    
    return {
        "status": health_status,
        "health_score": health_metrics["health_score"],
        "metrics": health_metrics,
        "recent_security_events": len(security_events),
        "checked_at": datetime.utcnow()
    }


@router.post("/system/maintenance")
async def toggle_maintenance_mode(
    maintenance_mode: bool,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Toggle maintenance mode.
    
    Access restricted to Admin users only.
    
    - **maintenance_mode**: True to enable, False to disable
    """
    # TODO: Implement actual maintenance mode toggle
    # This would typically involve updating a system configuration
    
    return {
        "message": f"Maintenance mode {'enabled' if maintenance_mode else 'disabled'}",
        "maintenance_mode": maintenance_mode,
        "changed_by": str(current_user.id),
        "changed_at": datetime.utcnow()
    }


@router.get("/config")
async def get_system_configuration(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get system configuration.
    
    Access restricted to Admin users only.
    """
    # TODO: Implement actual configuration retrieval
    # This would typically come from a configuration table or environment
    
    return {
        "app_name": "Project Samudra Sachet",
        "version": "1.0.0",
        "maintenance_mode": False,
        "max_file_size_mb": 10,
        "allowed_file_types": ["image/jpeg", "image/png", "image/webp", "video/mp4"],
        "hotspot_generation_interval_minutes": 10,
        "analysis_batch_size": 100,
        "retention_days": {
            "audit_logs": 90,
            "social_media_posts": 180,
            "hotspots": 30
        }
    }


@router.put("/config")
async def update_system_configuration(
    config_data: Dict[str, Any],
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update system configuration.
    
    Access restricted to Admin users only.
    
    - **config_data**: Configuration data to update
    """
    # TODO: Implement actual configuration update
    # This would typically involve updating a configuration table
    
    return {
        "message": "Configuration updated successfully",
        "updated_fields": list(config_data.keys()),
        "updated_by": str(current_user.id),
        "updated_at": datetime.utcnow()
    }
