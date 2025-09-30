from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import (
    get_current_active_user,
    require_citizen,
    require_official_roles
)
from app.db.session import get_db
from app.crud.crud_user import crud_user
from app.crud.crud_report import crud_report
from app.crud.crud_verification_log import crud_verification_log
from app.core.file_upload import upload_media_file
from app.schemas.verification_log import VerificationLogCreate, VerificationLogUpdate
from app.models.verification_log import VerificationDecision
from app.models.user import User
from app.models.report import ReportStatus, HazardType
from app.schemas.report import (
    Report as ReportSchema,
    ReportCreate,
    ReportUpdate,
    ReportSummary,
    ReportWithUser
)
import uuid
from datetime import datetime, timedelta


router = APIRouter()


@router.get("/public", response_model=List[ReportSummary])
async def list_public_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    hazard_type: Optional[HazardType] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Get public reports (no authentication required for citizens).
    """
    try:
        # Build query for public reports
        from sqlalchemy import select, and_, desc
        from app.models.report import Report
        
        query = select(Report)
        
        # Apply filters
        filters = []
        if hazard_type:
            filters.append(Report.hazard_type == hazard_type)
        
        # Only show verified or pending reports to public
        filters.append(Report.status.in_([ReportStatus.VERIFIED, ReportStatus.PENDING]))
        
        if filters:
            query = query.where(and_(*filters))
        
        # Apply sorting and pagination
        query = query.order_by(desc(Report.created_at)).offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        reports = result.scalars().all()
        
        # Convert to response format
        report_list = []
        for report in reports:
            # Parse location from WKT format for SQLite
            latitude, longitude = 0.0, 0.0
            if report.location and "POINT" in str(report.location):
                try:
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
        print(f"Public reports endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching public reports: {str(e)}"
        )


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_report(
    hazard_type: HazardType = Form(...),
    latitude: float = Form(..., ge=-90, le=90),
    longitude: float = Form(..., ge=-180, le=180),
    description: Optional[str] = Form(None),
    severity_level: int = Form(3, ge=1, le=5),
    media_file: Optional[UploadFile] = File(None),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a new hazard report - SIMPLIFIED VERSION.
    
    - **hazard_type**: Type of hazard being reported
    - **latitude**: GPS latitude (-90 to 90)
    - **longitude**: GPS longitude (-180 to 180)
    - **description**: Optional description of the hazard
    - **severity_level**: Severity level (1-5, default: 3)
    - **media_file**: Optional image or video file
    - **Authorization**: Bearer token in header
    """
    print(f"[REPORTS] Create report endpoint called")
    print(f"[REPORTS] Authorization header: {authorization}")
    
    # Check if authorization header is present
    if not authorization:
        print(f"[REPORTS] No authorization header provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required"
        )
    
    # Simple token validation
    if not authorization.startswith("Bearer "):
        print(f"[REPORTS] Invalid authorization format: {authorization}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format. Use 'Bearer <token>'"
        )
    
    token = authorization[7:]  # Remove "Bearer " prefix
    print(f"[REPORTS] Extracted token: {token[:20]}...")
    
    # Verify token and get user
    try:
        from app.core.security import verify_token
        from app.crud.crud_user import crud_user
        
        token_data = verify_token(token, "access")
        print(f"[REPORTS] Token verified: {token_data.email}")
        
        user = await crud_user.get_by_id(db, user_id=token_data.user_id)
        if not user:
            print(f"[REPORTS] User not found: {token_data.user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            print(f"[REPORTS] User inactive: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        print(f"[REPORTS] User authenticated: {user.email} ({user.user_role})")
        
    except Exception as e:
        print(f"[REPORTS] Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    # Handle file upload if provided
    media_url = None
    media_thumbnail_url = None
    
    if media_file:
        try:
            media_url, media_thumbnail_url = await upload_media_file(
                media_file, str(user.id)
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File upload failed: {str(e)}"
            )
    
    # Create report directly in database
    try:
        from app.models.report import Report, ReportStatus
        from app.core.config import settings
        
        # Create location point for SQLite
        if "postgresql" in settings.DATABASE_URL:
            from geoalchemy2 import functions as geo_func
            location_point = geo_func.ST_SetSRID(
                geo_func.ST_MakePoint(longitude, latitude), 
                4326
            )
        else:
            location_point = f"POINT({longitude} {latitude})"
        
        # Create report object
        db_report = Report(
            user_id=user.id,
            hazard_type=hazard_type,
            location=location_point,
            description=description,
            severity_level=severity_level,
            media_url=media_url,
            media_thumbnail_url=media_thumbnail_url,
            status=ReportStatus.PENDING
        )
        
        db.add(db_report)
        await db.commit()
        await db.refresh(db_report)
        
        print(f"[REPORTS] Report created successfully: ID {db_report.id}")
        
        # Return simple response
        return {
            "id": str(db_report.id),
            "message": "Report submitted successfully",
            "hazard_type": hazard_type.value,
            "latitude": latitude,
            "longitude": longitude,
            "description": description,
            "severity_level": severity_level,
            "status": "PENDING",
            "created_at": db_report.created_at.isoformat(),
            "user_email": user.email
        }
        
    except Exception as e:
        print(f"[REPORTS] Error creating report: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create report: {str(e)}"
        )


@router.get("/", response_model=List[ReportSummary])
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
    List reports with comprehensive filtering.
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **hazard_type**: Filter by hazard type
    - **status**: Filter by report status
    - **severity_min/max**: Filter by severity level range
    - **latitude/longitude/radius_km**: Filter by location
    - **date_from/date_to**: Filter by date range
    - **sort_by**: Sort field
    - **sort_order**: Sort direction (asc/desc)
    """
    reports, total_count = await crud_report.get_reports_with_filters(
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
    
    return reports


@router.get("/{report_id}", response_model=ReportWithUser)
async def get_report(
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get single report details.
    
    - **report_id**: Report UUID
    """
    report = await crud_report.get_by_id(db, report_id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Increment view count
    await crud_report.increment_view_count(db, report_id)
    
    return report


@router.put("/{report_id}", response_model=ReportSchema)
async def update_report(
    report_id: uuid.UUID,
    report_update: ReportUpdate,
    current_user: User = Depends(require_citizen),
    db: AsyncSession = Depends(get_db)
):
    """
    Update own report.
    
    - **report_id**: Report UUID
    - **report_update**: Updated report data
    """
    # Get report and check ownership
    report = await crud_report.get_by_id(db, report_id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if report.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own reports"
        )
    
    # Check if report can be updated (not verified)
    if report.status == ReportStatus.VERIFIED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update verified reports"
        )
    
    updated_report = await crud_report.update(db, report, report_update)
    return updated_report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: uuid.UUID,
    current_user: User = Depends(require_citizen),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete own report.
    
    - **report_id**: Report UUID
    """
    success = await crud_report.delete(db, report_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found or you don't have permission to delete it"
        )


@router.post("/{report_id}/vote", status_code=status.HTTP_200_OK)
async def vote_on_report(
    report_id: uuid.UUID,
    vote_type: str = Form(..., regex="^(upvote|downvote)$"),
    current_user: User = Depends(require_citizen),
    db: AsyncSession = Depends(get_db)
):
    """
    Vote on report credibility.
    
    - **report_id**: Report UUID
    - **vote_type**: Type of vote (upvote or downvote)
    """
    # Check if report exists
    report = await crud_report.get_by_id(db, report_id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check if user is voting on their own report
    if report.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot vote on your own report"
        )
    
    # Update vote counts
    updated_report = await crud_report.update_vote_counts(db, report_id, vote_type)
    if not updated_report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid vote type"
        )
    
    return {
        "message": f"Vote {vote_type} recorded successfully",
        "upvote_count": updated_report.upvote_count,
        "downvote_count": updated_report.downvote_count
    }


@router.get("/{report_id}/votes", status_code=status.HTTP_200_OK)
async def get_report_votes(
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get report vote summary.
    
    - **report_id**: Report UUID
    """
    report = await crud_report.get_by_id(db, report_id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return {
        "report_id": str(report_id),
        "upvote_count": report.upvote_count,
        "downvote_count": report.downvote_count,
        "total_votes": report.upvote_count + report.downvote_count,
        "net_score": report.upvote_count - report.downvote_count
    }


@router.post("/{report_id}/media", status_code=status.HTTP_200_OK)
async def upload_additional_media(
    report_id: uuid.UUID,
    media_file: UploadFile = File(...),
    current_user: User = Depends(require_citizen),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload additional media to existing report.
    
    - **report_id**: Report UUID
    - **media_file**: Additional media file
    """
    # Check if report exists and user owns it
    report = await crud_report.get_by_id(db, report_id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if report.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only add media to your own reports"
        )
    
    # Upload file
    try:
        media_url, media_thumbnail_url = await upload_media_file(
            media_file, str(current_user.id)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File upload failed: {str(e)}"
        )
    
    # Update report with new media
    report_update = ReportUpdate(
        media_url=media_url,
        media_thumbnail_url=media_thumbnail_url
    )
    
    updated_report = await crud_report.update(db, report, report_update)
    
    return {
        "message": "Additional media uploaded successfully",
        "media_url": updated_report.media_url,
        "media_thumbnail_url": updated_report.media_thumbnail_url
    }


@router.get("/nearby", response_model=List[ReportSummary])
async def get_nearby_reports(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10.0, gt=0, le=100),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get reports near a specific location.
    
    - **latitude**: GPS latitude
    - **longitude**: GPS longitude
    - **radius_km**: Search radius in kilometers
    - **limit**: Maximum number of reports to return
    """
    reports = await crud_report.get_reports_nearby(
        db=db,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        limit=limit
    )
    
    return reports


@router.get("/trending", response_model=List[ReportSummary])
async def get_trending_reports(
    hours: int = Query(24, ge=1, le=168),  # Max 1 week
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get trending/popular reports.
    
    - **hours**: Time window for trending (1-168 hours)
    - **limit**: Maximum number of reports to return
    """
    reports = await crud_report.get_trending_reports(
        db=db,
        hours=hours,
        limit=limit
    )
    
    return reports
