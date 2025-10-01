from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
from geoalchemy2 import functions as geo_func
from app.models.hotspot import Hotspot, HotspotStatus, HazardType
from app.models.report import Report, ReportStatus
from app.models.social_media_post import SocialMediaPost
from app.schemas.hotspot import HotspotCreate, HotspotUpdate
import uuid
from datetime import datetime, timedelta
import math


class CRUDHotspot:
    """CRUD operations for Hotspot model."""
    
    @staticmethod
    async def create(
        db: AsyncSession,
        hotspot_in: HotspotCreate
    ) -> Hotspot:
        """Create a new hotspot."""
        # Create PostGIS point from lat/lng
        location_point = geo_func.ST_SetSRID(
            geo_func.ST_MakePoint(hotspot_in.longitude, hotspot_in.latitude), 
            4326
        )
        
        db_hotspot = Hotspot(
            event_type=hotspot_in.event_type,
            location=location_point,
            radius_km=hotspot_in.radius_km,
            intensity_score=hotspot_in.intensity_score,
            alert_level=hotspot_in.alert_level,
            status=hotspot_in.status,
            first_reported_at=hotspot_in.first_reported_at,
            last_activity_at=hotspot_in.last_activity_at,
            expires_at=hotspot_in.expires_at,
            metadata=hotspot_in.metadata
        )
        
        db.add(db_hotspot)
        await db.commit()
        await db.refresh(db_hotspot)
        return db_hotspot
    
    @staticmethod
    async def get_by_id(db: AsyncSession, hotspot_id: uuid.UUID) -> Optional[Hotspot]:
        """Get hotspot by ID."""
        result = await db.execute(
            select(Hotspot).where(Hotspot.id == hotspot_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_active_hotspots(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        event_type: Optional[HazardType] = None,
        alert_level_min: Optional[int] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_km: Optional[float] = None
    ) -> Tuple[List[Hotspot], int]:
        """Get active hotspots with filtering."""
        query = select(Hotspot).where(Hotspot.status == HotspotStatus.ACTIVE)
        count_query = select(func.count(Hotspot.id)).where(Hotspot.status == HotspotStatus.ACTIVE)
        
        # Apply filters
        conditions = []
        
        if event_type:
            conditions.append(Hotspot.event_type == event_type)
        
        if alert_level_min is not None:
            conditions.append(Hotspot.alert_level >= alert_level_min)
        
        # Geospatial filtering
        if latitude is not None and longitude is not None and radius_km is not None:
            radius_meters = radius_km * 1000
            point = geo_func.ST_SetSRID(geo_func.ST_MakePoint(longitude, latitude), 4326)
            conditions.append(
                geo_func.ST_DWithin(
                    Hotspot.location,
                    point,
                    radius_meters
                )
            )
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Sort by intensity score (highest first)
        query = query.order_by(Hotspot.intensity_score.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute queries
        result = await db.execute(query)
        hotspots = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        return hotspots, total_count
    
    @staticmethod
    async def get_hotspots_for_map(
        db: AsyncSession,
        bounds: Optional[Dict[str, float]] = None,
        event_types: Optional[List[HazardType]] = None
    ) -> List[Hotspot]:
        """Get hotspots for map display."""
        query = select(Hotspot).where(Hotspot.status == HotspotStatus.ACTIVE)
        
        # Apply bounding box filter if provided
        if bounds:
            # Create bounding box geometry
            bbox = geo_func.ST_MakeEnvelope(
                bounds["west"], bounds["south"],
                bounds["east"], bounds["north"],
                4326
            )
            query = query.where(
                geo_func.ST_Intersects(Hotspot.location, bbox)
            )
        
        # Filter by event types if provided
        if event_types:
            query = query.where(Hotspot.event_type.in_(event_types))
        
        # Sort by intensity score
        query = query.order_by(Hotspot.intensity_score.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def update(
        db: AsyncSession,
        db_hotspot: Hotspot,
        hotspot_in: HotspotUpdate
    ) -> Hotspot:
        """Update hotspot."""
        update_data = hotspot_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_hotspot, field, value)
        
        await db.commit()
        await db.refresh(db_hotspot)
        return db_hotspot
    
    @staticmethod
    async def update_status(
        db: AsyncSession,
        hotspot_id: uuid.UUID,
        status: HotspotStatus
    ) -> Optional[Hotspot]:
        """Update hotspot status."""
        result = await db.execute(
            update(Hotspot)
            .where(Hotspot.id == hotspot_id)
            .values(status=status)
            .returning(Hotspot)
        )
        
        updated_hotspot = result.scalar_one_or_none()
        if updated_hotspot:
            await db.commit()
            await db.refresh(updated_hotspot)
        
        return updated_hotspot
    
    @staticmethod
    async def update_counts(
        db: AsyncSession,
        hotspot_id: uuid.UUID,
        report_count: Optional[int] = None,
        social_count: Optional[int] = None,
        verified_report_count: Optional[int] = None
    ) -> Optional[Hotspot]:
        """Update hotspot counts."""
        update_data = {}
        
        if report_count is not None:
            update_data["report_count"] = report_count
        if social_count is not None:
            update_data["social_count"] = social_count
        if verified_report_count is not None:
            update_data["verified_report_count"] = verified_report_count
        
        if not update_data:
            return None
        
        result = await db.execute(
            update(Hotspot)
            .where(Hotspot.id == hotspot_id)
            .values(**update_data)
            .returning(Hotspot)
        )
        
        updated_hotspot = result.scalar_one_or_none()
        if updated_hotspot:
            await db.commit()
            await db.refresh(updated_hotspot)
        
        return updated_hotspot
    
    @staticmethod
    async def get_reports_in_hotspot(
        db: AsyncSession,
        hotspot_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Report], int]:
        """Get reports within a hotspot."""
        # Get hotspot details
        hotspot = await CRUDHotspot.get_by_id(db, hotspot_id)
        if not hotspot:
            return [], 0
        
        # Calculate bounding box for hotspot
        radius_meters = hotspot.radius_km * 1000
        
        # Get reports within hotspot radius
        query = (
            select(Report)
            .options(selectinload(Report.user))
            .where(
                geo_func.ST_DWithin(
                    Report.location,
                    hotspot.location,
                    radius_meters
                )
            )
            .order_by(Report.created_at.desc())
        )
        
        count_query = select(func.count(Report.id)).where(
            geo_func.ST_DWithin(
                Report.location,
                hotspot.location,
                radius_meters
            )
        )
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute queries
        result = await db.execute(query)
        reports = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        return reports, total_count
    
    @staticmethod
    async def get_social_posts_in_hotspot(
        db: AsyncSession,
        hotspot_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[SocialMediaPost], int]:
        """Get social media posts within a hotspot."""
        # Get hotspot details
        hotspot = await CRUDHotspot.get_by_id(db, hotspot_id)
        if not hotspot:
            return [], 0
        
        # Calculate bounding box for hotspot
        radius_meters = hotspot.radius_km * 1000
        
        # Get posts within hotspot radius
        query = (
            select(SocialMediaPost)
            .where(
                geo_func.ST_DWithin(
                    SocialMediaPost.location,
                    hotspot.location,
                    radius_meters
                )
            )
            .order_by(SocialMediaPost.post_timestamp.desc())
        )
        
        count_query = select(func.count(SocialMediaPost.id)).where(
            geo_func.ST_DWithin(
                SocialMediaPost.location,
                hotspot.location,
                radius_meters
            )
        )
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute queries
        result = await db.execute(query)
        posts = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        return posts, total_count
    
    @staticmethod
    async def generate_hotspots_from_data(
        db: AsyncSession,
        hours: int = 6,
        min_reports: int = 3,
        cluster_radius_km: float = 5.0
    ) -> List[Hotspot]:
        """Generate hotspots from recent reports and social media data."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Get recent verified reports
        reports_query = (
            select(Report)
            .where(
                and_(
                    Report.created_at >= since,
                    Report.status == ReportStatus.VERIFIED,
                    Report.location.isnot(None)
                )
            )
        )
        
        reports_result = await db.execute(reports_query)
        reports = reports_result.scalars().all()
        
        # Get recent social media posts with location
        posts_query = (
            select(SocialMediaPost)
            .where(
                and_(
                    SocialMediaPost.post_timestamp >= since,
                    SocialMediaPost.location.isnot(None),
                    SocialMediaPost.relevance_score >= 0.7
                )
            )
        )
        
        posts_result = await db.execute(posts_query)
        posts = posts_result.scalars().all()
        
        # Simple clustering algorithm
        clusters = CRUDHotspot._cluster_points(reports, posts, cluster_radius_km)
        
        # Create hotspots for clusters with enough data points
        created_hotspots = []
        
        for cluster in clusters:
            if len(cluster["reports"]) + len(cluster["posts"]) >= min_reports:
                # Determine event type (most common hazard type)
                hazard_types = [r.hazard_type for r in cluster["reports"]]
                if hazard_types:
                    event_type = max(set(hazard_types), key=hazard_types.count)
                else:
                    event_type = HazardType.OTHER
                
                # Calculate intensity score
                intensity_score = CRUDHotspot._calculate_intensity_score(
                    cluster["reports"], cluster["posts"]
                )
                
                # Calculate alert level
                alert_level = CRUDHotspot._calculate_alert_level(intensity_score)
                
                # Create hotspot
                hotspot_data = HotspotCreate(
                    event_type=event_type,
                    latitude=cluster["center_lat"],
                    longitude=cluster["center_lng"],
                    radius_km=cluster_radius_km,
                    intensity_score=intensity_score,
                    alert_level=alert_level,
                    report_count=len(cluster["reports"]),
                    social_count=len(cluster["posts"]),
                    verified_report_count=len([r for r in cluster["reports"] if r.status == ReportStatus.VERIFIED]),
                    first_reported_at=min([r.created_at for r in cluster["reports"]] + [p.post_timestamp for p in cluster["posts"]]),
                    last_activity_at=max([r.created_at for r in cluster["reports"]] + [p.post_timestamp for p in cluster["posts"]]),
                    expires_at=datetime.utcnow() + timedelta(hours=24)
                )
                
                hotspot = await CRUDHotspot.create(db, hotspot_data)
                created_hotspots.append(hotspot)
        
        return created_hotspots
    
    @staticmethod
    def _cluster_points(reports: List[Report], posts: List[SocialMediaPost], radius_km: float) -> List[Dict]:
        """Simple clustering algorithm for geospatial points."""
        clusters = []
        radius_meters = radius_km * 1000
        
        # Combine all points
        all_points = []
        
        for report in reports:
            if report.location:
                # Extract coordinates from PostGIS geometry
                point = geo_func.ST_AsText(report.location)
                # This is simplified - in real implementation, extract lat/lng properly
                all_points.append({
                    "type": "report",
                    "data": report,
                    "lat": 0.0,  # Placeholder - would extract from geometry
                    "lng": 0.0   # Placeholder - would extract from geometry
                })
        
        for post in posts:
            if post.location:
                all_points.append({
                    "type": "post",
                    "data": post,
                    "lat": 0.0,  # Placeholder - would extract from geometry
                    "lng": 0.0   # Placeholder - would extract from geometry
                })
        
        # Simple clustering (in real implementation, use proper clustering algorithm)
        for point in all_points:
            # Find existing cluster or create new one
            assigned_cluster = None
            
            for cluster in clusters:
                # Calculate distance (simplified)
                distance = math.sqrt(
                    (point["lat"] - cluster["center_lat"])**2 + 
                    (point["lng"] - cluster["center_lng"])**2
                ) * 111000  # Rough conversion to meters
                
                if distance <= radius_meters:
                    assigned_cluster = cluster
                    break
            
            if assigned_cluster:
                # Add to existing cluster
                if point["type"] == "report":
                    assigned_cluster["reports"].append(point["data"])
                else:
                    assigned_cluster["posts"].append(point["data"])
                
                # Update center
                assigned_cluster["center_lat"] = (
                    assigned_cluster["center_lat"] * (len(assigned_cluster["reports"]) + len(assigned_cluster["posts"]) - 1) + 
                    point["lat"]
                ) / (len(assigned_cluster["reports"]) + len(assigned_cluster["posts"]))
                
                assigned_cluster["center_lng"] = (
                    assigned_cluster["center_lng"] * (len(assigned_cluster["reports"]) + len(assigned_cluster["posts"]) - 1) + 
                    point["lng"]
                ) / (len(assigned_cluster["reports"]) + len(assigned_cluster["posts"]))
            else:
                # Create new cluster
                new_cluster = {
                    "center_lat": point["lat"],
                    "center_lng": point["lng"],
                    "reports": [point["data"]] if point["type"] == "report" else [],
                    "posts": [point["data"]] if point["type"] == "post" else []
                }
                clusters.append(new_cluster)
        
        return clusters
    
    @staticmethod
    def _calculate_intensity_score(reports: List[Report], posts: List[SocialMediaPost]) -> float:
        """Calculate intensity score for a cluster."""
        # Base score from number of reports and posts
        base_score = min(len(reports) * 0.1 + len(posts) * 0.05, 0.5)
        
        # Boost from high severity reports
        severity_boost = sum(r.severity_level for r in reports) * 0.05
        
        # Boost from high engagement posts
        engagement_boost = sum(p.engagement_count for p in posts) * 0.0001
        
        # Combine scores
        intensity_score = min(base_score + severity_boost + engagement_boost, 1.0)
        
        return intensity_score
    
    @staticmethod
    def _calculate_alert_level(intensity_score: float) -> int:
        """Calculate alert level based on intensity score."""
        if intensity_score >= 0.8:
            return 5
        elif intensity_score >= 0.6:
            return 4
        elif intensity_score >= 0.4:
            return 3
        elif intensity_score >= 0.2:
            return 2
        else:
            return 1
    
    @staticmethod
    async def cleanup_expired_hotspots(db: AsyncSession) -> int:
        """Clean up expired hotspots."""
        result = await db.execute(
            delete(Hotspot).where(
                and_(
                    Hotspot.expires_at < datetime.utcnow(),
                    Hotspot.status == HotspotStatus.RESOLVED
                )
            )
        )
        
        deleted_count = result.rowcount
        await db.commit()
        
        return deleted_count
    
    @staticmethod
    async def delete(db: AsyncSession, hotspot_id: uuid.UUID) -> bool:
        """Delete hotspot."""
        result = await db.execute(
            select(Hotspot).where(Hotspot.id == hotspot_id)
        )
        hotspot = result.scalar_one_or_none()
        
        if not hotspot:
            return False
        
        await db.delete(hotspot)
        await db.commit()
        return True


# Create instance
crud_hotspot = CRUDHotspot()
