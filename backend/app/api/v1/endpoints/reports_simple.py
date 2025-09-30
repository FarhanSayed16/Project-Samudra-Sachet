from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc
from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.models.report import Report, ReportStatus, HazardType
from app.schemas.report import ReportSummary
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
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List reports with basic filtering.
    """
    try:
        # Build query
        query = select(Report)
        
        # Apply filters
        filters = []
        if hazard_type:
            filters.append(Report.hazard_type == hazard_type)
        if status:
            filters.append(Report.status == status)
        if severity_min:
            filters.append(Report.severity_level >= severity_min)
        if severity_max:
            filters.append(Report.severity_level <= severity_max)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Apply sorting
        query = query.order_by(desc(Report.created_at))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        reports = result.scalars().all()
        
        # Convert to dict format for JSON response
        report_list = []
        for report in reports:
            # Parse location from WKT format for SQLite
            latitude, longitude = 0.0, 0.0
            if report.location and "POINT" in str(report.location):
                try:
                    # Extract coordinates from WKT format: "POINT(lon lat)"
                    coords = str(report.location).replace("POINT(", "").replace(")", "").split()
                    if len(coords) >= 2:
                        longitude, latitude = float(coords[0]), float(coords[1])
                except (ValueError, IndexError):
                    pass
            
            report_dict = {
                "id": str(report.id),
                "hazard_type": report.hazard_type.value if report.hazard_type else None,
                "status": report.status.value if report.status else None,
                "latitude": latitude,
                "longitude": longitude,
                "description": report.description,
                "severity_level": report.severity_level,
                "confidence_score": float(report.confidence_score) if report.confidence_score else 0.0,
                "crowd_trust_score": float(report.crowd_trust_score) if report.crowd_trust_score else 0.0,
                "upvote_count": report.upvote_count,
                "downvote_count": report.downvote_count,
                "view_count": report.view_count,
                "created_at": report.created_at.isoformat() if report.created_at else None,
                "updated_at": report.updated_at.isoformat() if report.updated_at else None,
                "user_id": str(report.user_id) if report.user_id else None
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
        # Query all reports
        query = select(Report).order_by(desc(Report.created_at)).limit(100)
        result = await db.execute(query)
        reports = result.scalars().all()
        
        # Convert to simple dict format
        report_list = []
        for report in reports:
            # Parse location from WKT format for SQLite
            latitude, longitude = 0.0, 0.0
            if report.location and "POINT" in str(report.location):
                try:
                    # Extract coordinates from WKT format: "POINT(lon lat)"
                    coords = str(report.location).replace("POINT(", "").replace(")", "").split()
                    if len(coords) >= 2:
                        longitude, latitude = float(coords[0]), float(coords[1])
                except (ValueError, IndexError):
                    pass
            
            report_dict = {
                "id": str(report.id),
                "hazard_type": report.hazard_type.value if report.hazard_type else "unknown",
                "status": report.status.value if report.status else "pending",
                "latitude": latitude,
                "longitude": longitude,
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