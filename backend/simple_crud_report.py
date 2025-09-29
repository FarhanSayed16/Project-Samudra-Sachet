#!/usr/bin/env python3
"""
Simplified CRUD operations for SQLite compatibility
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from app.models.report import Report, ReportStatus, HazardType
from app.schemas.report import ReportCreate, ReportUpdate
import uuid
from datetime import datetime

class SimpleCRUDReport:
    """Simplified CRUD operations for Report model - SQLite compatible."""
    
    @staticmethod
    async def get_reports_with_filters(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        hazard_type: Optional[HazardType] = None,
        status: Optional[ReportStatus] = None,
        severity_min: Optional[int] = None,
        severity_max: Optional[int] = None,
        user_id: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_km: Optional[float] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Report], int]:
        """Get reports with basic filtering (no geospatial for SQLite)."""
        
        query = select(Report).options(selectinload(Report.user))
        count_query = select(func.count(Report.id))
        
        # Apply basic filters
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
            # Convert UUID string to string for comparison
            user_id_str = str(user_id) if user_id else None
            conditions.append(Report.user_id == user_id_str)
        
        if date_from:
            conditions.append(Report.created_at >= date_from)
        
        if date_to:
            conditions.append(Report.created_at <= date_to)
        
        # Note: Skipping geospatial filtering for SQLite compatibility
        # In a production environment, you'd use PostGIS or similar
        
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
        
        try:
            # Execute queries
            result = await db.execute(query)
            reports = result.scalars().all()
            
            count_result = await db.execute(count_query)
            total_count = count_result.scalar()
            
            return reports, total_count or 0
            
        except Exception as e:
            print(f"Database query error: {e}")
            return [], 0
    
    @staticmethod
    async def get_by_id(db: AsyncSession, report_id: str) -> Optional[Report]:
        """Get report by ID (string for SQLite)."""
        try:
            result = await db.execute(
                select(Report)
                .options(selectinload(Report.user))
                .where(Report.id == str(report_id))
            )
            return result.scalar_one_or_none()
        except Exception as e:
            print(f"Get report by ID error: {e}")
            return None
    
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Report]:
        """Get all reports with pagination."""
        try:
            result = await db.execute(
                select(Report)
                .options(selectinload(Report.user))
                .order_by(Report.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            print(f"Get all reports error: {e}")
            return []

# Create instance
simple_crud_report = SimpleCRUDReport()