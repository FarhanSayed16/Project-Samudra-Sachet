from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import (
    get_current_active_user,
    require_official_roles
)
from app.db.session import get_db
from app.crud.crud_social_media_post import crud_social_media_post
from app.crud.crud_media_analysis import crud_media_analysis
from app.models.user import User
from app.models.social_media_post import SocialPlatform, Sentiment, HazardType
from app.schemas.social_media_post import (
    SocialMediaPost as SocialMediaPostSchema,
    SocialMediaPostCreate,
    SocialMediaPostUpdate,
    SocialMediaPostSummary
)
import uuid
from datetime import datetime, timedelta


router = APIRouter()


@router.get("/public", response_model=List[SocialMediaPostSummary])
async def list_public_social_media_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    source: Optional[SocialPlatform] = Query(None),
    hazard_type: Optional[HazardType] = Query(None),
    sentiment: Optional[Sentiment] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Get public social media posts (no authentication required for citizens).
    """
    try:
        # Build query for public social media posts
        from sqlalchemy import select, and_, desc
        from app.models.social_media_post import SocialMediaPost
        
        query = select(SocialMediaPost)
        
        # Apply filters
        filters = []
        if source:
            filters.append(SocialMediaPost.source == source)
        if hazard_type:
            filters.append(SocialMediaPost.hazard_type == hazard_type)
        if sentiment:
            filters.append(SocialMediaPost.sentiment == sentiment)
        
        # Only show posts with high relevance score
        filters.append(SocialMediaPost.relevance_score >= 0.5)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Apply sorting and pagination
        query = query.order_by(desc(SocialMediaPost.created_at)).offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        posts = result.scalars().all()
        
        # Convert to response format
        post_list = []
        for post in posts:
            # Parse location from WKT format for SQLite
            latitude, longitude = 0.0, 0.0
            if post.location and "POINT" in str(post.location):
                try:
                    coords = str(post.location).replace("POINT(", "").replace(")", "").split()
                    if len(coords) >= 2:
                        longitude, latitude = float(coords[0]), float(coords[1])
                except (ValueError, IndexError):
                    pass
            
            post_dict = {
                "id": str(post.id),
                "source": post.source.value if post.source else None,
                "source_id": post.source_id,
                "post_text": post.post_text,
                "author_username": post.author_username,
                "post_timestamp": post.post_timestamp.isoformat() if post.post_timestamp else None,
                "location": {
                    "latitude": latitude,
                    "longitude": longitude
                } if latitude != 0.0 or longitude != 0.0 else None,
                "hazard_type": post.hazard_type.value if post.hazard_type else None,
                "sentiment": post.sentiment.value if post.sentiment else None,
                "sentiment_score": float(post.sentiment_score) if post.sentiment_score else 0.0,
                "engagement_count": post.engagement_count,
                "relevance_score": float(post.relevance_score) if post.relevance_score else 0.0,
                "created_at": post.created_at.isoformat() if post.created_at else None
            }
            post_list.append(post_dict)
        
        return post_list
    
    except Exception as e:
        print(f"Public social media posts endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching public social media posts: {str(e)}"
        )


@router.get("/", response_model=List[SocialMediaPostSummary])
async def list_social_media_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    source: Optional[SocialPlatform] = Query(None),
    hazard_type: Optional[HazardType] = Query(None),
    sentiment: Optional[Sentiment] = Query(None),
    relevance_min: Optional[float] = Query(None, ge=0.0, le=1.0),
    latitude: Optional[float] = Query(None, ge=-90, le=90),
    longitude: Optional[float] = Query(None, ge=-180, le=180),
    radius_km: Optional[float] = Query(None, gt=0, le=1000),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    language: Optional[str] = Query(None),
    sort_by: str = Query("post_timestamp", regex="^(post_timestamp|engagement_count|relevance_score|sentiment_score)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: User = Depends(require_official_roles),
    db: AsyncSession = Depends(get_db)
):
    """
    Query processed social media posts.
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **source**: Filter by social media platform
    - **hazard_type**: Filter by hazard type
    - **sentiment**: Filter by sentiment
    - **relevance_min**: Minimum relevance score
    - **latitude/longitude/radius_km**: Filter by location
    - **date_from/date_to**: Filter by date range
    - **language**: Filter by language
    - **sort_by**: Sort field
    - **sort_order**: Sort direction
    """
    posts, total_count = await crud_social_media_post.get_posts_with_filters(
        db=db,
        skip=skip,
        limit=limit,
        source=source,
        hazard_type=hazard_type,
        sentiment=sentiment,
        relevance_min=relevance_min,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        date_from=date_from,
        date_to=date_to,
        language=language,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    return posts


@router.get("/{post_id}", response_model=SocialMediaPostSchema)
async def get_social_media_post(
    post_id: uuid.UUID,
    current_user: User = Depends(require_official_roles),
    db: AsyncSession = Depends(get_db)
):
    """
    Get single social media post details.
    
    - **post_id**: Post UUID
    """
    post = await crud_social_media_post.get_by_id(db, post_id=post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Social media post not found"
        )
    
    return post


@router.get("/{post_id}/analysis")
async def get_post_analysis(
    post_id: uuid.UUID,
    current_user: User = Depends(require_official_roles),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI analysis results for a social media post.
    
    - **post_id**: Post UUID
    """
    # Check if post exists
    post = await crud_social_media_post.get_by_id(db, post_id=post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Social media post not found"
        )
    
    # Get analyses for this post
    analyses = await crud_media_analysis.get_by_post_id(db, post_id)
    
    return {
        "post_id": str(post_id),
        "analyses": analyses,
        "analysis_count": len(analyses)
    }


@router.post("/import", status_code=status.HTTP_201_CREATED)
async def import_social_media_batch(
    posts_data: List[SocialMediaPostCreate],
    current_user: User = Depends(require_official_roles),
    db: AsyncSession = Depends(get_db)
):
    """
    Ingest social media batch data.
    
    - **posts_data**: List of social media posts to import
    """
    imported_posts = []
    skipped_posts = []
    
    for post_data in posts_data:
        # Check if post already exists
        existing_post = await crud_social_media_post.get_by_source_id(db, post_data.source_id)
        
        if existing_post:
            skipped_posts.append({
                "source_id": post_data.source_id,
                "reason": "Post already exists"
            })
            continue
        
        try:
            post = await crud_social_media_post.create(db, post_data)
            imported_posts.append(post)
        except Exception as e:
            skipped_posts.append({
                "source_id": post_data.source_id,
                "reason": f"Import failed: {str(e)}"
            })
    
    return {
        "message": "Social media batch import completed",
        "imported_count": len(imported_posts),
        "skipped_count": len(skipped_posts),
        "imported_posts": [str(post.id) for post in imported_posts],
        "skipped_posts": skipped_posts
    }


@router.get("/trends")
async def get_trending_topics(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_official_roles),
    db: AsyncSession = Depends(get_db)
):
    """
    Get trending topics and hashtags.
    
    - **hours**: Time window for trending (1-168 hours)
    - **limit**: Maximum number of topics to return
    """
    # Get trending posts
    trending_posts = await crud_social_media_post.get_trending_posts(
        db=db,
        hours=hours,
        limit=limit
    )
    
    # Extract hashtags and topics (simplified implementation)
    hashtags = {}
    topics = {}
    
    for post in trending_posts:
        if post.post_text:
            # Simple hashtag extraction (in real implementation, use proper regex)
            words = post.post_text.split()
            for word in words:
                if word.startswith('#'):
                    hashtag = word.lower()
                    hashtags[hashtag] = hashtags.get(hashtag, 0) + 1
                elif word.startswith('@'):
                    continue  # Skip mentions
                else:
                    # Simple topic extraction
                    if len(word) > 3:
                        topic = word.lower()
                        topics[topic] = topics.get(topic, 0) + 1
    
    # Sort by frequency
    trending_hashtags = sorted(hashtags.items(), key=lambda x: x[1], reverse=True)[:10]
    trending_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "time_window_hours": hours,
        "trending_hashtags": [{"hashtag": h[0], "count": h[1]} for h in trending_hashtags],
        "trending_topics": [{"topic": t[0], "count": t[1]} for t in trending_topics],
        "total_posts_analyzed": len(trending_posts)
    }


@router.get("/sentiment")
async def get_sentiment_analysis(
    hours: int = Query(24, ge=1, le=168),
    hazard_type: Optional[HazardType] = Query(None),
    current_user: User = Depends(require_official_roles),
    db: AsyncSession = Depends(get_db)
):
    """
    Get sentiment analysis summary.
    
    - **hours**: Time window for analysis (1-168 hours)
    - **hazard_type**: Filter by specific hazard type
    """
    sentiment_stats = await crud_social_media_post.get_sentiment_analysis(
        db=db,
        hours=hours,
        hazard_type=hazard_type
    )
    
    return sentiment_stats


@router.post("/search")
async def search_social_media(
    search_query: str = Query(..., min_length=1, max_length=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_official_roles),
    db: AsyncSession = Depends(get_db)
):
    """
    Advanced semantic search in social media posts.
    
    - **search_query**: Search query string
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    posts, total_count = await crud_social_media_post.search_posts(
        db=db,
        search_query=search_query,
        skip=skip,
        limit=limit
    )
    
    return {
        "search_query": search_query,
        "results": posts,
        "total_count": total_count,
        "returned_count": len(posts)
    }
