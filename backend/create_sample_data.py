#!/usr/bin/env python3
"""
Script to populate the database with sample data for testing
"""
import asyncio
import sys
import os
import json
from datetime import datetime, timedelta
from uuid import uuid4

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.report import Report, HazardType, ReportStatus
from app.models.hotspot import Hotspot, HotspotStatus
from app.models.social_media_post import SocialMediaPost, SocialPlatform
from app.models.media_analysis import MediaAnalysis
from app.crud.crud_user import crud_user
from sqlalchemy import select

async def create_sample_data():
    """Create comprehensive sample data for the application"""
    
    async with AsyncSessionLocal() as db:
        try:
            print("🌊 Creating sample data for Project Samudra Sachet...")
            
            # Get existing users
            users = await crud_user.get_users(db, limit=10)
            if not users:
                print("❌ No users found. Please run the login fix first to create users.")
                return
            
            print(f"✅ Found {len(users)} users")
            
            # Create sample reports
            print("\n📊 Creating sample reports...")
            sample_reports = [
                {
                    "title": "Tsunami Warning - Mumbai Coast",
                    "description": "High wave activity detected near Mumbai coast",
                    "hazard_type": HazardType.TSUNAMI,
                    "latitude": 18.9220,
                    "longitude": 72.8347,
                    "severity_level": 5,  # Critical
                    "status": ReportStatus.VERIFIED,
                    "media_url": "https://example.com/tsunami.jpg"
                },
                {
                    "title": "High Waves at Juhu Beach",
                    "description": "Unusually high waves observed at Juhu Beach",
                    "hazard_type": HazardType.HIGH_WAVES,
                    "latitude": 19.1075,
                    "longitude": 72.8263,
                    "severity_level": 3,  # Medium
                    "status": ReportStatus.PENDING,
                    "media_url": "https://example.com/high-waves.jpg"
                },
                {
                    "title": "Coastal Flooding Alert",
                    "description": "Water levels rising beyond normal in coastal areas",
                    "hazard_type": HazardType.COASTAL_FLOODING,
                    "latitude": 19.0176,
                    "longitude": 72.8562,
                    "severity_level": 4,  # High
                    "status": ReportStatus.UNDER_REVIEW,
                    "media_url": "https://example.com/flooding.jpg"
                },
                {
                    "title": "Storm Surge Impact",
                    "description": "Significant storm surge affecting coastal structures",
                    "hazard_type": HazardType.STORM_SURGE,
                    "latitude": 18.9067,
                    "longitude": 72.8147,
                    "severity_level": 5,  # Critical
                    "status": ReportStatus.VERIFIED,
                    "media_url": "https://example.com/storm-surge.jpg"
                },
                {
                    "title": "Unusual Tide Patterns",
                    "description": "Abnormal tidal behavior observed in the area",
                    "hazard_type": HazardType.UNUSUAL_TIDE,
                    "latitude": 19.0330,
                    "longitude": 72.8697,
                    "severity_level": 2,  # Low-Medium
                    "status": ReportStatus.PENDING,
                    "media_url": "https://example.com/unusual-tide.jpg"
                }
            ]
            
            for i, report_data in enumerate(sample_reports):
                user = users[i % len(users)]  # Distribute reports among users
                
                # Create location point (WKT format for PostGIS/SQLite with spatial support)
                location_wkt = f"POINT({report_data['longitude']} {report_data['latitude']})"
                
                report = Report(
                    hazard_type=report_data["hazard_type"],
                    description=report_data["description"],
                    location=location_wkt,
                    severity_level=report_data["severity_level"],
                    status=report_data["status"],
                    media_url=report_data["media_url"],
                    user_id=user.id,
                    created_at=datetime.utcnow() - timedelta(days=i),
                    updated_at=datetime.utcnow() - timedelta(days=i)
                )
                
                db.add(report)
                print(f"   ✓ {report_data['title']}")
            
            # Create sample hotspots
            print("\n🔥 Creating sample hotspots...")
            sample_hotspots = [
                {
                    "name": "Mumbai Harbor Critical Zone",
                    "description": "High-risk area with tsunami and storm surge activity",
                    "latitude": 18.9220,
                    "longitude": 72.8347,
                    "radius": 5.0,  # 5km radius
                    "event_type": HazardType.TSUNAMI,
                    "intensity_score": 0.85,
                    "status": HotspotStatus.ACTIVE
                },
                {
                    "name": "Juhu Beach Wave Hotspot",
                    "description": "Area with consistent high wave activity",
                    "latitude": 19.1075,
                    "longitude": 72.8263,
                    "radius": 2.0,
                    "event_type": HazardType.HIGH_WAVES,
                    "intensity_score": 0.72,
                    "status": HotspotStatus.MONITORING
                },
                {
                    "name": "Coastal Flooding Zone",
                    "description": "Monitoring area for coastal flooding incidents",
                    "latitude": 19.0176,
                    "longitude": 72.8562,
                    "radius": 3.0,
                    "event_type": HazardType.COASTAL_FLOODING,
                    "intensity_score": 0.68,
                    "status": HotspotStatus.ACTIVE
                }
            ]
            
            for hotspot_data in sample_hotspots:
                # Create location point for hotspot
                location_wkt = f"POINT({hotspot_data['longitude']} {hotspot_data['latitude']})"
                
                hotspot = Hotspot(
                    event_type=hotspot_data["event_type"],
                    location=location_wkt,
                    radius_km=hotspot_data["radius"],
                    intensity_score=hotspot_data["intensity_score"],
                    status=hotspot_data["status"],
                    first_reported_at=datetime.utcnow() - timedelta(days=2),
                    last_activity_at=datetime.utcnow(),
                    created_at=datetime.utcnow() - timedelta(days=2),
                    updated_at=datetime.utcnow()
                )
                
                db.add(hotspot)
                print(f"   ✓ {hotspot_data['name']}")
            
            # Create sample social media posts
            print("\n📱 Creating sample social media posts...")
            sample_posts = [
                {
                    "platform": SocialPlatform.TWITTER,
                    "post_id": "1234567890",
                    "content": "Massive tsunami warning near Mumbai harbor! Everyone please stay safe. #TsunamiAlert #Mumbai",
                    "author_username": "@oceanwatcher",
                    "author_followers": 15000,
                    "engagement_score": 150.5,
                    "sentiment": "panic",
                    "relevance_score": 0.95,
                    "hazard_type": HazardType.TSUNAMI,
                    "latitude": 18.9220,
                    "longitude": 72.8347
                },
                {
                    "platform": SocialPlatform.INSTAGRAM,
                    "post_id": "ABC123XYZ",
                    "content": "Huge waves at Juhu Beach today! Be careful if you're near the coast. 🌊⚠️",
                    "author_username": "@cleanbeachinitiative",
                    "author_followers": 8500,
                    "engagement_score": 89.2,
                    "sentiment": "concern",
                    "relevance_score": 0.78,
                    "hazard_type": HazardType.HIGH_WAVES,
                    "latitude": 19.1075,
                    "longitude": 72.8263
                },
                {
                    "platform": SocialPlatform.FACEBOOK,
                    "post_id": "FB987654321",
                    "content": "Coastal flooding reported in several areas. Please avoid low-lying coastal roads.",
                    "author_username": "concerned_citizen_mumbai",
                    "author_followers": 450,
                    "engagement_score": 23.7,
                    "sentiment": "concern",
                    "relevance_score": 0.82,
                    "hazard_type": HazardType.COASTAL_FLOODING,
                    "latitude": 19.0176,
                    "longitude": 72.8562
                }
            ]
            
            for post_data in sample_posts:
                # Create location point for social media post
                location_wkt = f"POINT({post_data['longitude']} {post_data['latitude']})"
                
                post = SocialMediaPost(
                    source_id=post_data["post_id"],
                    source=post_data["platform"],
                    original_post=json.dumps({"raw_data": "sample_post", "content": post_data["content"]}),
                    post_text=post_data["content"],
                    author_username=post_data["author_username"],
                    post_timestamp=datetime.utcnow() - timedelta(hours=12),
                    location=location_wkt,
                    hazard_type=post_data["hazard_type"],
                    sentiment=post_data["sentiment"],
                    sentiment_score=0.5,  # Neutral baseline
                    engagement_count=int(post_data["engagement_score"]),
                    relevance_score=post_data["relevance_score"],
                    created_at=datetime.utcnow() - timedelta(hours=6),
                    updated_at=datetime.utcnow() - timedelta(hours=6)
                )
                
                db.add(post)
                print(f"   ✓ {post_data['platform'].value} post by {post_data['author_username']}")
            
            # Commit all changes
            await db.commit()
            
            # Verify data creation
            reports_count = len((await db.execute(select(Report))).scalars().all())
            hotspots_count = len((await db.execute(select(Hotspot))).scalars().all())
            posts_count = len((await db.execute(select(SocialMediaPost))).scalars().all())
            
            print(f"\n✅ Sample data created successfully!")
            print(f"   📊 Reports: {reports_count}")
            print(f"   🔥 Hotspots: {hotspots_count}")
            print(f"   📱 Social Media Posts: {posts_count}")
            print(f"   👥 Users: {len(users)}")
            
        except Exception as e:
            print(f"❌ Error creating sample data: {e}")
            await db.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(create_sample_data())