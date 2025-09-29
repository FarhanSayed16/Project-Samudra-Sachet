from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.models.report import ReportStatus, HazardType
from app.schemas.report import ReportSummary
import sys
import os

# Add backend directory to path to import simple_crud_report
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(backend_path)

from simple_crud_report import simple_crud_report
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[dict])
async def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    hazard_type: Optional[HazardType] = Query(None),
    status: Optional[ReportStatus] = Query(None),
    severity_min: Optional[int] = Query(None, ge=1, le=5),
    severity_max: Optional[int] = Query(None, ge=1, le=5),
    latitude: Optional[float] = Query(None, ge=-90, le=90),
    longitude: Optional[float] = Query(None, ge=-180, le=180),
    radius_km: Optional[float] = Query(None, gt=0, le=1000),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    sort_by: str = Query("created_at", regex="^(created_at|severity_level|confidence_score|crowd_trust_score)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List reports with basic filtering (SQLite compatible).
    """
    try:
        reports, total_count = await simple_crud_report.get_reports_with_filters(
            db=db,
            skip=skip,
            limit=limit,
            hazard_type=hazard_type,
            status=status,
            severity_min=severity_min,
            severity_max=severity_max,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Convert to dict format for JSON response
        report_list = []
        for report in reports:
            report_dict = {
                "id": str(report.id),
                "hazard_type": report.hazard_type.value if report.hazard_type else None,
                "status": report.status.value if report.status else None,
                "latitude": report.latitude,
                "longitude": report.longitude,
                "description": report.description,
                "severity_level": report.severity_level,
                "confidence_score": report.confidence_score,
                "crowd_trust_score": report.crowd_trust_score,
                "upvote_count": report.upvote_count,
                "downvote_count": report.downvote_count,
                "view_count": report.view_count,
                "created_at": report.created_at.isoformat() if report.created_at else None,
                "updated_at": report.updated_at.isoformat() if report.updated_at else None,
                "user": {
                    "id": str(report.user.id) if report.user else None,
                    "username": report.user.username if report.user else None,
                    "role": report.user.role.value if report.user and report.user.role else None
                } if report.user else None
            }
            report_list.append(report_dict)
        
        return report_list
    
    except Exception as e:
        print(f"Reports endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching reports: {str(e)}"
        )

@router.get("/simple", response_model=List[dict])
async def get_simple_reports(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all reports in simple format.
    """
    try:
        reports = await simple_crud_report.get_all(db, skip=0, limit=100)
        
        # Convert to simple dict format
        report_list = []
        for report in reports:
            report_dict = {
                "id": str(report.id),
                "hazard_type": report.hazard_type.value if report.hazard_type else "unknown",
                "status": report.status.value if report.status else "pending",
                "latitude": float(report.latitude) if report.latitude else 0.0,
                "longitude": float(report.longitude) if report.longitude else 0.0,
                "description": report.description or "",
                "severity_level": report.severity_level or 3,
                "created_at": report.created_at.isoformat() if report.created_at else None,
                "user_id": str(report.user_id) if report.user_id else None
            }
            report_list.append(report_dict)
        
        return report_list
    
    except Exception as e:
        print(f"Simple reports endpoint error: {e}")
        return [{"error": f"Database error: {str(e)}"}]