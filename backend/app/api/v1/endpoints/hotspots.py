from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import (
    get_current_active_user,
    require_analyst_or_authority,
    require_authority_or_admin
)
from app.db.session import get_db
from app.crud.crud_hotspot import crud_hotspot
from app.crud.crud_report import crud_report
from app.crud.crud_social_media_post import crud_social_media_post
from app.models.user import User
from app.models.hotspot import HotspotStatus, HazardType
from app.schemas.hotspot import (
    Hotspot as HotspotSchema,
    HotspotCreate,
    HotspotUpdate,
    HotspotSummary
)
import uuid
from datetime import datetime, timedelta


router = APIRouter()


@router.get("/", response_model=List[HotspotSummary])
async def list_hotspots(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    event_type: Optional[HazardType] = Query(None),
    alert_level_min: Optional[int] = Query(None, ge=1, le=5),
    latitude: Optional[float] = Query(None, ge=-90, le=90),
    longitude: Optional[float] = Query(None, ge=-180, le=180),
    radius_km: Optional[float] = Query(None, gt=0, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    List active hotspots.
    
    Public endpoint for dashboard and mobile app.
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **event_type**: Filter by hazard type
    - **alert_level_min**: Minimum alert level
    - **latitude/longitude/radius_km**: Filter by location
    """
    hotspots, total_count = await crud_hotspot.get_active_hotspots(
        db=db,
        skip=skip,
        limit=limit,
        event_type=event_type,
        alert_level_min=alert_level_min,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km
    )
    
    return hotspots


@router.get("/{hotspot_id}", response_model=HotspotSchema)
async def get_hotspot(
    hotspot_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get hotspot details.
    
    Public endpoint for dashboard and mobile app.
    
    - **hotspot_id**: Hotspot UUID
    """
    hotspot = await crud_hotspot.get_by_id(db, hotspot_id=hotspot_id)
    if not hotspot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hotspot not found"
        )
    
    return hotspot


@router.post("/", response_model=HotspotSchema, status_code=status.HTTP_201_CREATED)
async def create_hotspot(
    hotspot_data: HotspotCreate,
    current_user: User = Depends(require_authority_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Create manual hotspot.
    
    Access restricted to Authority and Admin users.
    
    - **hotspot_data**: Hotspot creation data
    """
    hotspot = await crud_hotspot.create(db, hotspot_data)
    return hotspot


@router.put("/{hotspot_id}", response_model=HotspotSchema)
async def update_hotspot(
    hotspot_id: uuid.UUID,
    hotspot_update: HotspotUpdate,
    current_user: User = Depends(require_analyst_or_authority),
    db: AsyncSession = Depends(get_db)
):
    """
    Update hotspot status and information.
    
    Access restricted to Analyst, Authority, and Admin users.
    
    - **hotspot_id**: Hotspot UUID
    - **hotspot_update**: Updated hotspot data
    """
    # Check if hotspot exists
    hotspot = await crud_hotspot.get_by_id(db, hotspot_id=hotspot_id)
    if not hotspot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hotspot not found"
        )
    
    updated_hotspot = await crud_hotspot.update(db, hotspot, hotspot_update)
    return updated_hotspot


@router.delete("/{hotspot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hotspot(
    hotspot_id: uuid.UUID,
    current_user: User = Depends(require_authority_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Resolve/archive hotspot.
    
    Access restricted to Authority and Admin users.
    
    - **hotspot_id**: Hotspot UUID
    """
    success = await crud_hotspot.delete(db, hotspot_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hotspot not found"
        )


@router.get("/{hotspot_id}/reports")
async def get_hotspot_reports(
    hotspot_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get reports within a hotspot.
    
    - **hotspot_id**: Hotspot UUID
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    reports, total_count = await crud_hotspot.get_reports_in_hotspot(
        db=db,
        hotspot_id=hotspot_id,
        skip=skip,
        limit=limit
    )
    
    return {
        "hotspot_id": str(hotspot_id),
        "reports": reports,
        "total_count": total_count,
        "returned_count": len(reports)
    }


@router.get("/{hotspot_id}/social-media")
async def get_hotspot_social_media(
    hotspot_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_analyst_or_authority),
    db: AsyncSession = Depends(get_db)
):
    """
    Get social media posts within a hotspot.
    
    Access restricted to Analyst, Authority, and Admin users.
    
    - **hotspot_id**: Hotspot UUID
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    posts, total_count = await crud_hotspot.get_social_posts_in_hotspot(
        db=db,
        hotspot_id=hotspot_id,
        skip=skip,
        limit=limit
    )
    
    return {
        "hotspot_id": str(hotspot_id),
        "posts": posts,
        "total_count": total_count,
        "returned_count": len(posts)
    }


@router.post("/{hotspot_id}/alerts", status_code=status.HTTP_200_OK)
async def send_hotspot_alert(
    hotspot_id: uuid.UUID,
    alert_message: str = Form(..., min_length=1, max_length=500),
    alert_level: int = Form(..., ge=1, le=5),
    current_user: User = Depends(require_authority_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Send targeted alert for a hotspot.
    
    Access restricted to Authority and Admin users.
    
    - **hotspot_id**: Hotspot UUID
    - **alert_message**: Alert message to send
    - **alert_level**: Alert level (1-5)
    """
    # Check if hotspot exists
    hotspot = await crud_hotspot.get_by_id(db, hotspot_id=hotspot_id)
    if not hotspot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hotspot not found"
        )
    
    # TODO: Implement actual alert sending (push notifications, SMS, etc.)
    # For now, return mock response
    
    return {
        "message": "Alert sent successfully",
        "hotspot_id": str(hotspot_id),
        "alert_message": alert_message,
        "alert_level": alert_level,
        "sent_by": str(current_user.id),
        "recipients_count": 0  # Would be actual count in real implementation
    }


@router.get("/map-data")
async def get_hotspots_for_map(
    west: float = Query(..., ge=-180, le=180),
    south: float = Query(..., ge=-90, le=90),
    east: float = Query(..., ge=-180, le=180),
    north: float = Query(..., ge=-90, le=90),
    event_types: Optional[str] = Query(None),  # Comma-separated list
    db: AsyncSession = Depends(get_db)
):
    """
    Get hotspots for map display.
    
    Public endpoint optimized for map rendering.
    
    - **west/south/east/north**: Bounding box coordinates
    - **event_types**: Comma-separated list of hazard types to filter
    """
    bounds = {
        "west": west,
        "south": south,
        "east": east,
        "north": north
    }
    
    # Parse event types if provided
    parsed_event_types = None
    if event_types:
        try:
            parsed_event_types = [HazardType(et.strip()) for et in event_types.split(",")]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event types provided"
            )
    
    hotspots = await crud_hotspot.get_hotspots_for_map(
        db=db,
        bounds=bounds,
        event_types=parsed_event_types
    )
    
    return {
        "bounds": bounds,
        "hotspots": hotspots,
        "count": len(hotspots)
    }


@router.post("/generate", status_code=status.HTTP_200_OK)
async def generate_hotspots(
    hours: int = Form(6, ge=1, le=168),
    min_reports: int = Form(3, ge=1, le=20),
    cluster_radius_km: float = Form(5.0, gt=0, le=50),
    current_user: User = Depends(require_authority_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate hotspots from recent data.
    
    Access restricted to Authority and Admin users.
    
    - **hours**: Time window for data collection (1-168 hours)
    - **min_reports**: Minimum reports/posts required for hotspot
    - **cluster_radius_km**: Clustering radius in kilometers
    """
    try:
        created_hotspots = await crud_hotspot.generate_hotspots_from_data(
            db=db,
            hours=hours,
            min_reports=min_reports,
            cluster_radius_km=cluster_radius_km
        )
        
        return {
            "message": "Hotspot generation completed",
            "created_hotspots": len(created_hotspots),
            "parameters": {
                "hours": hours,
                "min_reports": min_reports,
                "cluster_radius_km": cluster_radius_km
            },
            "hotspot_ids": [str(h.id) for h in created_hotspots]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hotspot generation failed: {str(e)}"
        )


@router.post("/cleanup", status_code=status.HTTP_200_OK)
async def cleanup_expired_hotspots(
    current_user: User = Depends(require_authority_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Clean up expired hotspots.
    
    Access restricted to Authority and Admin users.
    """
    deleted_count = await crud_hotspot.cleanup_expired_hotspots(db)
    
    return {
        "message": "Hotspot cleanup completed",
        "deleted_hotspots": deleted_count
    }
