#!/usr/bin/env python3
"""
Database initialization script for Project Samudra Sachet.
Creates the database tables and initial admin user.
"""
import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.db.session import AsyncSessionLocal, init_db
from app.models.user import User, UserRole
from app.models.report import Report, ReportStatus, HazardType
from app.models.hotspot import Hotspot, HotspotStatus
from app.models.social_media_post import SocialMediaPost, SocialPlatform, Sentiment
from app.crud.crud_user import crud_user
from app.crud.crud_report import crud_report
from app.crud.crud_hotspot import crud_hotspot
from app.crud.crud_social_media_post import crud_social_media_post
from app.core.config import settings
from sqlalchemy import select
import uuid
import json

async def create_admin_user():
    """Create the default admin user if it doesn't exist."""
    
    async with AsyncSessionLocal() as db:
        try:
            print("Checking for admin user...")
            
            # Check if admin user already exists
            admin_user = await crud_user.get_by_email(db, "admin@samudra-sachet.com")
            
            if admin_user:
                print("Admin user already exists")
                return admin_user
            
            # Create admin user
            from app.schemas.user import UserCreate
            
            admin_data = UserCreate(
                email="admin@samudra-sachet.com",
                password="admin123",
                full_name="System Administrator",
                user_role=UserRole.ADMIN,
                language_preference="en"
            )
            
            admin_user = await crud_user.create(db, admin_data)
            print("Admin user created successfully")
            print(f"   Email: admin@samudra-sachet.com")
            print(f"   Password: admin123")
            print(f"   Role: {admin_user.user_role.value}")
            
            return admin_user
            
        except Exception as e:
            print(f"Error creating admin user: {e}")
            await db.rollback()
            raise

async def create_demo_users():
    """Create demo users for testing."""
    
    async with AsyncSessionLocal() as db:
        try:
            print("\nCreating demo users...")
            
            demo_users = [
                # Citizens
                {
                    "email": "citizen@samudra-sachet.com",
                    "password": "citizen123",
                    "full_name": "John Citizen",
                    "user_role": UserRole.CITIZEN
                },
                {
                    "email": "citizen2@samudra-sachet.com",
                    "password": "citizen123",
                    "full_name": "Maria Santos",
                    "user_role": UserRole.CITIZEN
                },
                {
                    "email": "citizen3@samudra-sachet.com",
                    "password": "citizen123",
                    "full_name": "Ahmed Hassan",
                    "user_role": UserRole.CITIZEN
                },
                # Coastal Volunteers
                {
                    "email": "volunteer@samudra-sachet.com",
                    "password": "volunteer123",
                    "full_name": "Sarah Volunteer",
                    "user_role": UserRole.COASTAL_VOLUNTEER,
                    "organization": "Mumbai Coastal Volunteers",
                    "verification_id": "VOL-2024-001"
                },
                {
                    "email": "volunteer2@samudra-sachet.com",
                    "password": "volunteer123",
                    "full_name": "Rajesh Kumar",
                    "user_role": UserRole.COASTAL_VOLUNTEER,
                    "organization": "Goa Coastal Watch",
                    "verification_id": "VOL-2024-002"
                },
                {
                    "email": "volunteer3@samudra-sachet.com",
                    "password": "volunteer123",
                    "full_name": "Priya Sharma",
                    "user_role": UserRole.COASTAL_VOLUNTEER,
                    "organization": "Chennai Marine Rescue",
                    "verification_id": "VOL-2024-003"
                },
                # Coastal Guards
                {
                    "email": "guard@samudra-sachet.com",
                    "password": "guard123",
                    "full_name": "Captain Rajesh",
                    "user_role": UserRole.COASTAL_GUARD,
                    "organization": "Mumbai Coastal Guard",
                    "verification_id": "CG-2024-001"
                },
                {
                    "email": "guard2@samudra-sachet.com",
                    "password": "guard123",
                    "full_name": "Captain Singh",
                    "user_role": UserRole.COASTAL_GUARD,
                    "organization": "Indian Coast Guard",
                    "verification_id": "CG-2024-002"
                },
                {
                    "email": "guard3@samudra-sachet.com",
                    "password": "guard123",
                    "full_name": "Lt. Commander Patel",
                    "user_role": UserRole.COASTAL_GUARD,
                    "organization": "Navy Coastal Division",
                    "verification_id": "CG-2024-003"
                },
                # Disaster Managers
                {
                    "email": "manager@samudra-sachet.com",
                    "password": "manager123",
                    "full_name": "Dr. Priya Sharma",
                    "user_role": UserRole.DISASTER_MANAGER,
                    "organization": "Disaster Management Authority",
                    "verification_id": "DM-2024-001"
                },
                {
                    "email": "manager2@samudra-sachet.com",
                    "password": "manager123",
                    "full_name": "Dr. Arjun Reddy",
                    "user_role": UserRole.DISASTER_MANAGER,
                    "organization": "NDMA Regional Office",
                    "verification_id": "DM-2024-002"
                },
                {
                    "email": "manager3@samudra-sachet.com",
                    "password": "manager123",
                    "full_name": "Commander Nair",
                    "user_role": UserRole.DISASTER_MANAGER,
                    "organization": "Emergency Response Team",
                    "verification_id": "DM-2024-003"
                }
            ]
            
            from app.schemas.user import UserCreate
            
            for user_data in demo_users:
                # Check if user already exists
                existing_user = await crud_user.get_by_email(db, user_data["email"])
                if existing_user:
                    print(f"   - {user_data['email']} already exists")
                    continue
                
                # Create user
                user_create = UserCreate(**user_data)
                user = await crud_user.create(db, user_create)
                print(f"   - Created {user_data['email']} ({user_data['user_role']})")
            
            print("Demo users created successfully")
            
        except Exception as e:
            print(f"Error creating demo users: {e}")
            await db.rollback()
            raise

async def create_sample_reports():
    """Create sample reports for testing."""
    
    async with AsyncSessionLocal() as db:
        try:
            print("\nCreating sample reports...")
            
            # Get users for report creation
            citizen_user = await crud_user.get_by_email(db, "citizen@samudra-sachet.com")
            volunteer_user = await crud_user.get_by_email(db, "volunteer@samudra-sachet.com")
            
            if not citizen_user or not volunteer_user:
                print("   - Demo users not found, skipping sample reports")
                return
            
            sample_reports = [
                {
                    "description": "High Waves at Juhu Beach - Unusually high waves observed at Juhu Beach around 3 PM. Water level rising rapidly.",
                    "hazard_type": HazardType.HIGH_WAVES,
                    "severity_level": 4,
                    "location": "POINT(72.8263 19.1074)",
                    "status": ReportStatus.VERIFIED,
                    "user_id": citizen_user.id
                },
                {
                    "description": "Coastal Flooding in Versova - Heavy rainfall causing coastal flooding in Versova area. Roads are waterlogged.",
                    "hazard_type": HazardType.COASTAL_FLOODING,
                    "severity_level": 3,
                    "location": "POINT(72.8125 19.1356)",
                    "status": ReportStatus.PENDING,
                    "user_id": citizen_user.id
                },
                {
                    "description": "Storm Surge Warning - Strong winds and storm surge expected in the next 2 hours. Residents advised to stay indoors.",
                    "hazard_type": HazardType.STORM_SURGE,
                    "severity_level": 5,
                    "location": "POINT(72.8777 19.0760)",
                    "status": ReportStatus.VERIFIED,
                    "user_id": volunteer_user.id
                },
                {
                    "description": "Unusual Tide Pattern - Tide levels are 2 meters higher than normal. Beach access restricted.",
                    "hazard_type": HazardType.UNUSUAL_TIDE,
                    "severity_level": 2,
                    "location": "POINT(72.8562 19.0176)",
                    "status": ReportStatus.PENDING,
                    "user_id": citizen_user.id
                }
            ]
            
            for report_data in sample_reports:
                # Check if report already exists (by description)
                existing_reports = await db.execute(
                    select(Report).where(Report.description == report_data["description"])
                )
                if existing_reports.scalar_one_or_none():
                    print(f"   - Report already exists")
                    continue
                
                # Create report
                report = Report(**report_data)
                db.add(report)
                print(f"   - Created report: {report_data['hazard_type'].value}")
            
            await db.commit()
            print("Sample reports created successfully")
            
        except Exception as e:
            print(f"Error creating sample reports: {e}")
            await db.rollback()
            raise

async def create_sample_hotspots():
    """Create sample hotspots for testing."""
    
    async with AsyncSessionLocal() as db:
        try:
            print("\nCreating sample hotspots...")
            
            # Get users for hotspot creation
            guard_user = await crud_user.get_by_email(db, "guard@samudra-sachet.com")
            manager_user = await crud_user.get_by_email(db, "manager@samudra-sachet.com")
            
            if not guard_user or not manager_user:
                print("   - Demo users not found, skipping sample hotspots")
                return
            
            sample_hotspots = [
                {
                    "event_type": HazardType.HIGH_WAVES,
                    "location": "POINT(72.8263 19.1074)",
                    "radius_km": 0.5,
                    "intensity_score": 0.8,
                    "alert_level": 4,
                    "report_count": 3,
                    "status": HotspotStatus.ACTIVE
                },
                {
                    "event_type": HazardType.COASTAL_FLOODING,
                    "location": "POINT(72.8125 19.1356)",
                    "radius_km": 0.3,
                    "intensity_score": 0.6,
                    "alert_level": 3,
                    "report_count": 2,
                    "status": HotspotStatus.ACTIVE
                },
                {
                    "event_type": HazardType.STORM_SURGE,
                    "location": "POINT(72.8777 19.0760)",
                    "radius_km": 0.2,
                    "intensity_score": 0.9,
                    "alert_level": 5,
                    "report_count": 1,
                    "status": HotspotStatus.ACTIVE
                }
            ]
            
            for hotspot_data in sample_hotspots:
                # Check if hotspot already exists (by event_type and location)
                existing_hotspots = await db.execute(
                    select(Hotspot).where(
                        Hotspot.event_type == hotspot_data["event_type"]
                    )
                )
                if existing_hotspots.scalar_one_or_none():
                    print(f"   - Hotspot already exists")
                    continue
                
                # Create hotspot
                hotspot = Hotspot(**hotspot_data)
                db.add(hotspot)
                print(f"   - Created hotspot: {hotspot_data['event_type'].value}")
            
            await db.commit()
            print("Sample hotspots created successfully")
            
        except Exception as e:
            print(f"Error creating sample hotspots: {e}")
            await db.rollback()
            raise

async def create_sample_social_media_posts():
    """Create sample social media posts for testing."""
    
    async with AsyncSessionLocal() as db:
        try:
            print("\nCreating sample social media posts...")
            
            sample_posts = [
                {
                    "source_id": "twitter_1234567890",
                    "source": SocialPlatform.TWITTER,
                    "post_text": "High waves at Juhu Beach today! Stay safe everyone #MumbaiWeather #CoastalSafety",
                    "author_username": "@MumbaiWeather",
                    "post_timestamp": datetime.now(),
                    "hazard_type": HazardType.HIGH_WAVES,
                    "sentiment": Sentiment.NEUTRAL,
                    "relevance_score": 0.8,
                    "location": "POINT(72.8263 19.1074)",
                    "post_url": "https://twitter.com/MumbaiWeather/status/1234567890",
                    "original_post": json.dumps({"id": "1234567890", "text": "High waves at Juhu Beach today! Stay safe everyone #MumbaiWeather #CoastalSafety"})
                },
                {
                    "source_id": "facebook_1234567890",
                    "source": SocialPlatform.FACEBOOK,
                    "post_text": "Coastal flooding reported in Versova area. Avoid the roads if possible. #MumbaiFloods #StaySafe",
                    "author_username": "Mumbai Coastal Updates",
                    "post_timestamp": datetime.now(),
                    "hazard_type": HazardType.COASTAL_FLOODING,
                    "sentiment": Sentiment.CONCERN,
                    "relevance_score": 0.9,
                    "location": "POINT(72.8125 19.1356)",
                    "post_url": "https://facebook.com/MumbaiCoastalUpdates/posts/1234567890",
                    "original_post": json.dumps({"id": "1234567890", "message": "Coastal flooding reported in Versova area. Avoid the roads if possible. #MumbaiFloods #StaySafe"})
                },
                {
                    "source_id": "instagram_1234567890",
                    "source": SocialPlatform.INSTAGRAM,
                    "post_text": "Beautiful sunset at Marine Drive, but be careful of the high tide! #MumbaiLife #CoastalBeauty",
                    "author_username": "@MumbaiLife",
                    "post_timestamp": datetime.now(),
                    "hazard_type": HazardType.UNUSUAL_TIDE,
                    "sentiment": Sentiment.AWARENESS,
                    "relevance_score": 0.6,
                    "location": "POINT(72.8777 19.0760)",
                    "post_url": "https://instagram.com/p/1234567890",
                    "original_post": json.dumps({"id": "1234567890", "caption": "Beautiful sunset at Marine Drive, but be careful of the high tide! #MumbaiLife #CoastalBeauty"})
                },
                {
                    "source_id": "twitter_1234567891",
                    "source": SocialPlatform.TWITTER,
                    "post_text": "Storm surge warning issued for Mumbai coast. Residents advised to stay indoors. #StormWarning #MumbaiSafety",
                    "author_username": "@IMDMumbai",
                    "post_timestamp": datetime.now(),
                    "hazard_type": HazardType.STORM_SURGE,
                    "sentiment": Sentiment.CONCERN,
                    "relevance_score": 0.95,
                    "location": "POINT(72.8777 19.0760)",
                    "post_url": "https://twitter.com/IMDMumbai/status/1234567891",
                    "original_post": json.dumps({"id": "1234567891", "text": "Storm surge warning issued for Mumbai coast. Residents advised to stay indoors. #StormWarning #MumbaiSafety"})
                }
            ]
            
            for post_data in sample_posts:
                # Check if post already exists
                existing_posts = await db.execute(
                    select(SocialMediaPost).where(SocialMediaPost.source_id == post_data["source_id"])
                )
                if existing_posts.scalar_one_or_none():
                    print(f"   - Post already exists")
                    continue
                
                # Create post
                post = SocialMediaPost(**post_data)
                db.add(post)
                print(f"   - Created post from {post_data['author_username']}")
            
            await db.commit()
            print("Sample social media posts created successfully")
            
        except Exception as e:
            print(f"Error creating sample social media posts: {e}")
            await db.rollback()
            raise

async def main():
    """Initialize the database and create default users."""
    
    print("Project Samudra Sachet - Database Initialization")
    print("=" * 60)
    print(f"Database URL: {settings.DATABASE_URL}")
    
    try:
        # Initialize database tables
        print("\nInitializing database tables...")
        await init_db()
        print("Database tables initialized successfully")
        
        # Create admin user
        await create_admin_user()
        
        # Create demo users
        await create_demo_users()
        
        # Create sample data
        await create_sample_reports()
        await create_sample_hotspots()
        await create_sample_social_media_posts()
        
        print("\nDatabase initialization completed successfully!")
        print("\nDefault Login Credentials:")
        print("   Admin: admin@samudra-sachet.com / admin123")
        print("   Citizens: citizen@samudra-sachet.com / citizen123")
        print("            citizen2@samudra-sachet.com / citizen123")
        print("            citizen3@samudra-sachet.com / citizen123")
        print("   Coastal Volunteers: volunteer@samudra-sachet.com / volunteer123")
        print("                      volunteer2@samudra-sachet.com / volunteer123")
        print("                      volunteer3@samudra-sachet.com / volunteer123")
        print("   Coastal Guards: guard@samudra-sachet.com / guard123")
        print("                  guard2@samudra-sachet.com / guard123")
        print("                  guard3@samudra-sachet.com / guard123")
        print("   Disaster Managers: manager@samudra-sachet.com / manager123")
        print("                     manager2@samudra-sachet.com / manager123")
        print("                     manager3@samudra-sachet.com / manager123")
        print("\nSample Data Created:")
        print("   • 4 Sample Reports (2 verified, 2 pending)")
        print("   • 3 Sample Hotspots (all active)")
        print("   • 4 Sample Social Media Posts")
        print("   • 13 Demo Users across all roles")
        print("   • All data linked to appropriate user roles")
        
    except Exception as e:
        print(f"\nDatabase initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
