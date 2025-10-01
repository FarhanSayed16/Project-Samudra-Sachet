from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_
from sqlalchemy.orm import selectinload
from app.models.media_analysis import MediaAnalysis, AnalysisType
from app.models.report import Report
from app.models.social_media_post import SocialMediaPost
from app.schemas.media_analysis import MediaAnalysisCreate, MediaAnalysisUpdate
import uuid
from datetime import datetime, timedelta


class CRUDMediaAnalysis:
    """CRUD operations for MediaAnalysis model."""
    
    @staticmethod
    async def create(
        db: AsyncSession,
        analysis_in: MediaAnalysisCreate
    ) -> MediaAnalysis:
        """Create a new media analysis."""
        db_analysis = MediaAnalysis(
            report_id=analysis_in.report_id,
            post_id=analysis_in.post_id,
            analysis_type=analysis_in.analysis_type,
            ai_model_name=analysis_in.ai_model_name,
            ai_model_version=analysis_in.ai_model_version,
            results=analysis_in.results,
            processing_time_ms=analysis_in.processing_time_ms
        )
        
        db.add(db_analysis)
        await db.commit()
        await db.refresh(db_analysis)
        return db_analysis
    
    @staticmethod
    async def get_by_id(db: AsyncSession, analysis_id: uuid.UUID) -> Optional[MediaAnalysis]:
        """Get media analysis by ID."""
        result = await db.execute(
            select(MediaAnalysis)
            .options(selectinload(MediaAnalysis.report))
            .options(selectinload(MediaAnalysis.social_media_post))
            .where(MediaAnalysis.id == analysis_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_report_id(
        db: AsyncSession,
        report_id: uuid.UUID
    ) -> List[MediaAnalysis]:
        """Get all analyses for a report."""
        result = await db.execute(
            select(MediaAnalysis)
            .where(MediaAnalysis.report_id == report_id)
            .order_by(MediaAnalysis.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_by_post_id(
        db: AsyncSession,
        post_id: uuid.UUID
    ) -> List[MediaAnalysis]:
        """Get all analyses for a social media post."""
        result = await db.execute(
            select(MediaAnalysis)
            .where(MediaAnalysis.post_id == post_id)
            .order_by(MediaAnalysis.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_analyses_with_filters(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        analysis_type: Optional[AnalysisType] = None,
        ai_model_name: Optional[str] = None,
        report_id: Optional[uuid.UUID] = None,
        post_id: Optional[uuid.UUID] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[MediaAnalysis], int]:
        """Get media analyses with filtering."""
        query = select(MediaAnalysis).options(
            selectinload(MediaAnalysis.report),
            selectinload(MediaAnalysis.social_media_post)
        )
        count_query = select(func.count(MediaAnalysis.id))
        
        # Apply filters
        conditions = []
        
        if analysis_type:
            conditions.append(MediaAnalysis.analysis_type == analysis_type)
        
        if ai_model_name:
            conditions.append(MediaAnalysis.ai_model_name == ai_model_name)
        
        if report_id:
            conditions.append(MediaAnalysis.report_id == report_id)
        
        if post_id:
            conditions.append(MediaAnalysis.post_id == post_id)
        
        if date_from:
            conditions.append(MediaAnalysis.created_at >= date_from)
        
        if date_to:
            conditions.append(MediaAnalysis.created_at <= date_to)
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Apply sorting
        if sort_by == "created_at":
            sort_column = MediaAnalysis.created_at
        elif sort_by == "processing_time_ms":
            sort_column = MediaAnalysis.processing_time_ms
        else:
            sort_column = MediaAnalysis.created_at
        
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute queries
        result = await db.execute(query)
        analyses = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        return analyses, total_count
    
    @staticmethod
    async def get_analysis_jobs(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> Tuple[List[MediaAnalysis], int]:
        """Get analysis jobs (for background processing)."""
        query = select(MediaAnalysis)
        count_query = select(func.count(MediaAnalysis.id))
        
        # Filter by status if provided
        if status:
            # This would need to be implemented based on job status tracking
            pass
        
        query = query.order_by(MediaAnalysis.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        analyses = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        return analyses, total_count
    
    @staticmethod
    async def get_analysis_stats(
        db: AsyncSession,
        hours: int = 24,
        analysis_type: Optional[AnalysisType] = None
    ) -> Dict[str, Any]:
        """Get analysis statistics."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        query = select(MediaAnalysis).where(MediaAnalysis.created_at >= since)
        
        if analysis_type:
            query = query.where(MediaAnalysis.analysis_type == analysis_type)
        
        result = await db.execute(query)
        analyses = result.scalars().all()
        
        # Calculate statistics
        total_analyses = len(analyses)
        type_counts = {}
        total_processing_time = 0
        analyses_with_processing_time = 0
        
        for analysis in analyses:
            type_counts[analysis.analysis_type.value] = type_counts.get(analysis.analysis_type.value, 0) + 1
            
            if analysis.processing_time_ms:
                total_processing_time += analysis.processing_time_ms
                analyses_with_processing_time += 1
        
        avg_processing_time = total_processing_time / analyses_with_processing_time if analyses_with_processing_time > 0 else 0
        
        return {
            "total_analyses": total_analyses,
            "type_counts": type_counts,
            "average_processing_time_ms": avg_processing_time,
            "time_window_hours": hours
        }
    
    @staticmethod
    async def update(
        db: AsyncSession,
        db_analysis: MediaAnalysis,
        analysis_in: MediaAnalysisUpdate
    ) -> MediaAnalysis:
        """Update media analysis."""
        update_data = analysis_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_analysis, field, value)
        
        await db.commit()
        await db.refresh(db_analysis)
        return db_analysis
    
    @staticmethod
    async def batch_create(
        db: AsyncSession,
        analyses_data: List[MediaAnalysisCreate]
    ) -> List[MediaAnalysis]:
        """Create multiple analyses in batch."""
        db_analyses = []
        
        for analysis_data in analyses_data:
            db_analysis = MediaAnalysis(
                report_id=analysis_data.report_id,
                post_id=analysis_data.post_id,
                analysis_type=analysis_data.analysis_type,
                ai_model_name=analysis_data.ai_model_name,
                ai_model_version=analysis_data.ai_model_version,
                results=analysis_data.results,
                processing_time_ms=analysis_data.processing_time_ms
            )
            db_analyses.append(db_analysis)
        
        db.add_all(db_analyses)
        await db.commit()
        
        for db_analysis in db_analyses:
            await db.refresh(db_analysis)
        
        return db_analyses
    
    @staticmethod
    async def delete(db: AsyncSession, analysis_id: uuid.UUID) -> bool:
        """Delete media analysis."""
        result = await db.execute(
            select(MediaAnalysis).where(MediaAnalysis.id == analysis_id)
        )
        analysis = result.scalar_one_or_none()
        
        if not analysis:
            return False
        
        await db.delete(analysis)
        await db.commit()
        return True
    
    @staticmethod
    async def get_available_models(db: AsyncSession) -> List[Dict[str, Any]]:
        """Get list of available AI models."""
        # This would typically come from a configuration or external service
        # For now, return a static list
        return [
            {
                "model_id": "hazard_classifier_v1",
                "name": "Hazard Classifier v1",
                "type": "image_classification",
                "description": "Classifies images for hazard detection",
                "version": "1.0.0",
                "status": "active"
            },
            {
                "model_id": "sentiment_analyzer_v1",
                "name": "Sentiment Analyzer v1",
                "type": "sentiment_analysis",
                "description": "Analyzes text sentiment",
                "version": "1.0.0",
                "status": "active"
            },
            {
                "model_id": "ner_extractor_v1",
                "name": "NER Extractor v1",
                "type": "ner_extraction",
                "description": "Extracts named entities from text",
                "version": "1.0.0",
                "status": "active"
            }
        ]


# Create instance
crud_media_analysis = CRUDMediaAnalysis()
