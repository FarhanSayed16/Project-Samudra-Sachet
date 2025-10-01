from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, or_
from sqlalchemy.orm import selectinload
from geoalchemy2 import functions as geo_func
from geoalchemy2.shape import to_shape
from shapely.geometry import Point
from app.models.report import Report, ReportStatus, HazardType
from app.models.user import User
from app.schemas.report import ReportCreate, ReportUpdate
from app.db.base_class import BaseModel
import uuid
from datetime import datetime, timedelta


class CRUDReport:
    """CRUD operations for Report model."""
    
    @staticmethod
    async def create(
        db: AsyncSession, 
        report_in: ReportCreate, 
        user_id: uuid.UUID,
        media_url: Optional[str] = None,
        media_thumbnail_url: Optional[str] = None
    ) -> Report:
        """Create a new report."""
        from app.core.config import settings
        
        # Create location point based on database type
        if "postgresql" in settings.DATABASE_URL:
            # Use PostGIS for PostgreSQL
            location_point = geo_func.ST_SetSRID(
                geo_func.ST_MakePoint(report_in.longitude, report_in.latitude), 
                4326
            )
        else:
            # Use WKT for SQLite
            location_point = f"POINT({report_in.longitude} {report_in.latitude})"
        
        db_report = Report(
            user_id=user_id,
            hazard_type=report_in.hazard_type,
            location=location_point,
            description=report_in.description,
            severity_level=report_in.severity_level,
            media_url=media_url,
            media_thumbnail_url=media_thumbnail_url,
            status=ReportStatus.PENDING
        )
        
        db.add(db_report)
        await db.commit()
        await db.refresh(db_report)
        return db_report
    
    @staticmethod
    async def get_by_id(db: AsyncSession, report_id: uuid.UUID) -> Optional[Report]:
        """Get report by ID."""
        result = await db.execute(
            select(Report)
            .options(selectinload(Report.user))
            .options(selectinload(Report.verification_logs))
            .where(Report.id == report_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_reports_with_filters(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        hazard_type: Optional[HazardType] = None,
        status: Optional[ReportStatus] = None,
        severity_min: Optional[int] = None,
        severity_max: Optional[int] = None,
        user_id: Optional[uuid.UUID] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_km: Optional[float] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Report], int]:
        """Get reports with comprehensive filtering and pagination."""
        query = select(Report).options(selectinload(Report.user))
        count_query = select(func.count(Report.id))
        
        # Apply filters
        conditions = []
        
        if hazard_type:
            conditions.append(Report.hazard_type == hazard_type)
        
        if status:
            conditions.append(Report.status == status)
        
        if severity_min is not None:
            conditions.append(Report.severity_level >= severity_min)
        
        if severity_max is not None:
            conditions.append(Report.severity_level <= severity_max)
        
        if user_id:
            conditions.append(Report.user_id == user_id)
        
        if date_from:
            conditions.append(Report.created_at >= date_from)
        
        if date_to:
            conditions.append(Report.created_at <= date_to)
        
        # Geospatial filtering
        if latitude is not None and longitude is not None and radius_km is not None:
            # Convert km to meters for PostGIS
            radius_meters = radius_km * 1000
            point = geo_func.ST_SetSRID(geo_func.ST_MakePoint(longitude, latitude), 4326)
            conditions.append(
                geo_func.ST_DWithin(
                    Report.location,
                    point,
                    radius_meters
                )
            )
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Apply sorting
        if sort_by == "created_at":
            sort_column = Report.created_at
        elif sort_by == "severity_level":
            sort_column = Report.severity_level
        elif sort_by == "confidence_score":
            sort_column = Report.confidence_score
        elif sort_by == "crowd_trust_score":
            sort_column = Report.crowd_trust_score
        else:
            sort_column = Report.created_at
        
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute queries
        result = await db.execute(query)
        reports = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        return reports, total_count
    
    @staticmethod
    async def get_reports_nearby(
        db: AsyncSession,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0,
        limit: int = 50
    ) -> List[Report]:
        """Get reports within a specific radius of a location."""
        radius_meters = radius_km * 1000
        point = geo_func.ST_SetSRID(geo_func.ST_MakePoint(longitude, latitude), 4326)
        
        query = (
            select(Report)
            .options(selectinload(Report.user))
            .where(
                geo_func.ST_DWithin(
                    Report.location,
                    point,
                    radius_meters
                )
            )
            .order_by(Report.created_at.desc())
            .limit(limit)
        )
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_trending_reports(
        db: AsyncSession,
        hours: int = 24,
        limit: int = 20
    ) -> List[Report]:
        """Get trending reports based on engagement."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        query = (
            select(Report)
            .options(selectinload(Report.user))
            .where(Report.created_at >= since)
            .order_by(
                (Report.upvote_count - Report.downvote_count).desc(),
                Report.view_count.desc()
            )
            .limit(limit)
        )
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def update(
        db: AsyncSession, 
        db_report: Report, 
        report_in: ReportUpdate
    ) -> Report:
        """Update report information."""
        update_data = report_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_report, field, value)
        
        await db.commit()
        await db.refresh(db_report)
        return db_report
    
    @staticmethod
    async def update_status(
        db: AsyncSession, 
        report_id: uuid.UUID, 
        status: ReportStatus
    ) -> Optional[Report]:
        """Update report status."""
        result = await db.execute(
            update(Report)
            .where(Report.id == report_id)
            .values(status=status)
            .returning(Report)
        )
        
        updated_report = result.scalar_one_or_none()
        if updated_report:
            await db.commit()
            await db.refresh(updated_report)
        
        return updated_report
    
    @staticmethod
    async def increment_view_count(db: AsyncSession, report_id: uuid.UUID) -> None:
        """Increment report view count."""
        await db.execute(
            update(Report)
            .where(Report.id == report_id)
            .values(view_count=Report.view_count + 1)
        )
        await db.commit()
    
    @staticmethod
    async def update_vote_counts(
        db: AsyncSession, 
        report_id: uuid.UUID, 
        vote_type: str
    ) -> Optional[Report]:
        """Update report vote counts."""
        if vote_type == "upvote":
            update_field = Report.upvote_count
        elif vote_type == "downvote":
            update_field = Report.downvote_count
        else:
            return None
        
        result = await db.execute(
            update(Report)
            .where(Report.id == report_id)
            .values(**{update_field.name: update_field + 1})
            .returning(Report)
        )
        
        updated_report = result.scalar_one_or_none()
        if updated_report:
            await db.commit()
            await db.refresh(updated_report)
        
        return updated_report
    
    @staticmethod
    async def update_confidence_score(
        db: AsyncSession, 
        report_id: uuid.UUID, 
        confidence_score: float
    ) -> Optional[Report]:
        """Update AI confidence score."""
        result = await db.execute(
            update(Report)
            .where(Report.id == report_id)
            .values(confidence_score=confidence_score)
            .returning(Report)
        )
        
        updated_report = result.scalar_one_or_none()
        if updated_report:
            await db.commit()
            await db.refresh(updated_report)
        
        return updated_report
    
    @staticmethod
    async def update_crowd_trust_score(
        db: AsyncSession, 
        report_id: uuid.UUID, 
        crowd_trust_score: float
    ) -> Optional[Report]:
        """Update crowd trust score."""
        result = await db.execute(
            update(Report)
            .where(Report.id == report_id)
            .values(crowd_trust_score=crowd_trust_score)
            .returning(Report)
        )
        
        updated_report = result.scalar_one_or_none()
        if updated_report:
            await db.commit()
            await db.refresh(updated_report)
        
        return updated_report
    
    @staticmethod
    async def delete(db: AsyncSession, report_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Delete report (only by owner)."""
        result = await db.execute(
            select(Report).where(
                and_(Report.id == report_id, Report.user_id == user_id)
            )
        )
        report = result.scalar_one_or_none()
        
        if not report:
            return False
        
        await db.delete(report)
        await db.commit()
        return True
    
    @staticmethod
    async def get_user_reports(
        db: AsyncSession,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Report], int]:
        """Get reports by specific user."""
        return await CRUDReport.get_reports_with_filters(
            db=db,
            skip=skip,
            limit=limit,
            user_id=user_id
        )


# Create instance
crud_report = CRUDReport()


# Convenience functions for backward compatibility
async def create_report(db: AsyncSession, report_in: ReportCreate, user_id: uuid.UUID) -> Report:
    """Create a new report (convenience function)."""
    return await crud_report.create(db, report_in, user_id)


async def get_report_by_id(db: AsyncSession, report_id: uuid.UUID) -> Optional[Report]:
    """Get report by ID (convenience function)."""
    return await crud_report.get_by_id(db, report_id)
