from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, or_
from sqlalchemy.orm import selectinload
from geoalchemy2 import functions as geo_func
from app.models.social_media_post import SocialMediaPost, SocialPlatform, Sentiment, HazardType
from app.schemas.social_media_post import SocialMediaPostCreate, SocialMediaPostUpdate
import uuid
from datetime import datetime, timedelta


class CRUDSocialMediaPost:
    """CRUD operations for SocialMediaPost model."""
    
    @staticmethod
    async def create(
        db: AsyncSession,
        post_in: SocialMediaPostCreate
    ) -> SocialMediaPost:
        """Create a new social media post."""
        # Create PostGIS point from lat/lng if provided
        location_point = None
        if post_in.latitude is not None and post_in.longitude is not None:
            location_point = geo_func.ST_SetSRID(
                geo_func.ST_MakePoint(post_in.longitude, post_in.latitude), 
                4326
            )
        
        db_post = SocialMediaPost(
            source_id=post_in.source_id,
            source=post_in.source,
            original_post=post_in.original_post,
            post_text=post_in.post_text,
            post_url=post_in.post_url,
            author_username=post_in.author_username,
            author_verified=post_in.author_verified,
            post_timestamp=post_in.post_timestamp,
            language=post_in.language,
            location=location_point,
            location_entities=post_in.location_entities,
            hazard_type=post_in.hazard_type,
            sentiment=post_in.sentiment,
            sentiment_score=post_in.sentiment_score,
            engagement_count=post_in.engagement_count,
            repost_count=post_in.repost_count,
            relevance_score=post_in.relevance_score
        )
        
        db.add(db_post)
        await db.commit()
        await db.refresh(db_post)
        return db_post
    
    @staticmethod
    async def get_by_id(db: AsyncSession, post_id: uuid.UUID) -> Optional[SocialMediaPost]:
        """Get social media post by ID."""
        result = await db.execute(
            select(SocialMediaPost).where(SocialMediaPost.id == post_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_source_id(db: AsyncSession, source_id: str) -> Optional[SocialMediaPost]:
        """Get social media post by source ID."""
        result = await db.execute(
            select(SocialMediaPost).where(SocialMediaPost.source_id == source_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_posts_with_filters(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        source: Optional[SocialPlatform] = None,
        hazard_type: Optional[HazardType] = None,
        sentiment: Optional[Sentiment] = None,
        relevance_min: Optional[float] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_km: Optional[float] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        language: Optional[str] = None,
        sort_by: str = "post_timestamp",
        sort_order: str = "desc"
    ) -> Tuple[List[SocialMediaPost], int]:
        """Get social media posts with comprehensive filtering."""
        query = select(SocialMediaPost)
        count_query = select(func.count(SocialMediaPost.id))
        
        # Apply filters
        conditions = []
        
        if source:
            conditions.append(SocialMediaPost.source == source)
        
        if hazard_type:
            conditions.append(SocialMediaPost.hazard_type == hazard_type)
        
        if sentiment:
            conditions.append(SocialMediaPost.sentiment == sentiment)
        
        if relevance_min is not None:
            conditions.append(SocialMediaPost.relevance_score >= relevance_min)
        
        if language:
            conditions.append(SocialMediaPost.language == language)
        
        if date_from:
            conditions.append(SocialMediaPost.post_timestamp >= date_from)
        
        if date_to:
            conditions.append(SocialMediaPost.post_timestamp <= date_to)
        
        # Geospatial filtering
        if latitude is not None and longitude is not None and radius_km is not None:
            radius_meters = radius_km * 1000
            point = geo_func.ST_SetSRID(geo_func.ST_MakePoint(longitude, latitude), 4326)
            conditions.append(
                geo_func.ST_DWithin(
                    SocialMediaPost.location,
                    point,
                    radius_meters
                )
            )
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Apply sorting
        if sort_by == "post_timestamp":
            sort_column = SocialMediaPost.post_timestamp
        elif sort_by == "engagement_count":
            sort_column = SocialMediaPost.engagement_count
        elif sort_by == "relevance_score":
            sort_column = SocialMediaPost.relevance_score
        elif sort_by == "sentiment_score":
            sort_column = SocialMediaPost.sentiment_score
        else:
            sort_column = SocialMediaPost.post_timestamp
        
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute queries
        result = await db.execute(query)
        posts = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        return posts, total_count
    
    @staticmethod
    async def get_trending_posts(
        db: AsyncSession,
        hours: int = 24,
        limit: int = 20
    ) -> List[SocialMediaPost]:
        """Get trending social media posts."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        query = (
            select(SocialMediaPost)
            .where(SocialMediaPost.post_timestamp >= since)
            .order_by(SocialMediaPost.engagement_count.desc())
            .limit(limit)
        )
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_sentiment_analysis(
        db: AsyncSession,
        hours: int = 24,
        hazard_type: Optional[HazardType] = None
    ) -> Dict[str, Any]:
        """Get sentiment analysis summary."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        query = select(SocialMediaPost).where(SocialMediaPost.post_timestamp >= since)
        
        if hazard_type:
            query = query.where(SocialMediaPost.hazard_type == hazard_type)
        
        result = await db.execute(query)
        posts = result.scalars().all()
        
        # Calculate sentiment statistics
        sentiment_counts = {}
        total_sentiment_score = 0
        posts_with_sentiment = 0
        
        for post in posts:
            if post.sentiment:
                sentiment_counts[post.sentiment.value] = sentiment_counts.get(post.sentiment.value, 0) + 1
            
            if post.sentiment_score is not None:
                total_sentiment_score += post.sentiment_score
                posts_with_sentiment += 1
        
        avg_sentiment_score = total_sentiment_score / posts_with_sentiment if posts_with_sentiment > 0 else 0
        
        return {
            "total_posts": len(posts),
            "posts_with_sentiment": posts_with_sentiment,
            "sentiment_counts": sentiment_counts,
            "average_sentiment_score": avg_sentiment_score,
            "time_window_hours": hours
        }
    
    @staticmethod
    async def update(
        db: AsyncSession,
        db_post: SocialMediaPost,
        post_in: SocialMediaPostUpdate
    ) -> SocialMediaPost:
        """Update social media post."""
        update_data = post_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_post, field, value)
        
        await db.commit()
        await db.refresh(db_post)
        return db_post
    
    @staticmethod
    async def update_analysis_results(
        db: AsyncSession,
        post_id: uuid.UUID,
        hazard_type: Optional[HazardType] = None,
        sentiment: Optional[Sentiment] = None,
        sentiment_score: Optional[float] = None,
        relevance_score: Optional[float] = None
    ) -> Optional[SocialMediaPost]:
        """Update AI analysis results."""
        update_data = {}
        
        if hazard_type is not None:
            update_data["hazard_type"] = hazard_type
        if sentiment is not None:
            update_data["sentiment"] = sentiment
        if sentiment_score is not None:
            update_data["sentiment_score"] = sentiment_score
        if relevance_score is not None:
            update_data["relevance_score"] = relevance_score
        
        if not update_data:
            return None
        
        result = await db.execute(
            update(SocialMediaPost)
            .where(SocialMediaPost.id == post_id)
            .values(**update_data)
            .returning(SocialMediaPost)
        )
        
        updated_post = result.scalar_one_or_none()
        if updated_post:
            await db.commit()
            await db.refresh(updated_post)
        
        return updated_post
    
    @staticmethod
    async def search_posts(
        db: AsyncSession,
        search_query: str,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[SocialMediaPost], int]:
        """Search posts by text content."""
        query = (
            select(SocialMediaPost)
            .where(
                or_(
                    SocialMediaPost.post_text.ilike(f"%{search_query}%"),
                    SocialMediaPost.author_username.ilike(f"%{search_query}%")
                )
            )
            .order_by(SocialMediaPost.post_timestamp.desc())
        )
        
        count_query = select(func.count(SocialMediaPost.id)).where(
            or_(
                SocialMediaPost.post_text.ilike(f"%{search_query}%"),
                SocialMediaPost.author_username.ilike(f"%{search_query}%")
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
    async def delete(db: AsyncSession, post_id: uuid.UUID) -> bool:
        """Delete social media post."""
        result = await db.execute(
            select(SocialMediaPost).where(SocialMediaPost.id == post_id)
        )
        post = result.scalar_one_or_none()
        
        if not post:
            return False
        
        await db.delete(post)
        await db.commit()
        return True


# Create instance
crud_social_media_post = CRUDSocialMediaPost()
